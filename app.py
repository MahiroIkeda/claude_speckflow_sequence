"""
SpecFlow — 仕様駆動開発アシスタント (Claude Code 内完結版)

旧版との違い：
  - Anthropic API への直接呼び出しを廃止し、Claude Code CLI (`claude -p`) を subprocess で呼ぶ
  - GitHub REST API への直接呼び出しを廃止し、`gh` CLI と `git` コマンドを使う
  - 結果として `.env` の ANTHROPIC_API_KEY と GITHUB_TOKEN は不要
  - すべての AI ロジックは `.claude/skills/` の Skill としても直接呼べる

起動：
  python app.py
  → http://localhost:5000
"""

from flask import Flask, request, jsonify, render_template
from datetime import datetime
from pathlib import Path
import json
import shutil
import subprocess

app = Flask(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent
PROMPTS_DIR = PROJECT_ROOT / "prompts"
DOCS_DIR = PROJECT_ROOT / "docs"

# ════════════════════════════════
#  Claude Code CLI 呼び出し
# ════════════════════════════════

def _claude_executable():
    for name in ("claude", "claude.cmd", "claude.exe"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError(
        "Claude Code CLI (`claude`) が PATH に見つかりません。"
        "Claude Code をインストールし、`claude` が実行可能であることを確認してください。"
    )


def call_claude(user_message, system_prompt=None, history=None, max_tokens=None):
    """Claude Code CLI を subprocess で呼び出す共通関数。

    Anthropic API は使わない。プロンプトは stdin で渡し、コマンドライン長制限を回避する。
    max_tokens は互換のため引数に残しているが、CLI 側では指定しない。
    """
    parts = []
    if system_prompt:
        parts.append("【SYSTEM】\n" + system_prompt + "\n")
    if history:
        for msg in history:
            role = (msg.get("role") or "user").upper()
            parts.append(f"【{role}】\n{msg.get('content', '')}\n")
    parts.append("【USER】\n" + user_message + "\n")
    full_prompt = "\n".join(parts)

    cmd = [_claude_executable(), "-p"]
    try:
        result = subprocess.run(
            cmd,
            input=full_prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=600,
            cwd=str(PROJECT_ROOT),
        )
    except subprocess.TimeoutExpired:
        raise RuntimeError("Claude Code CLI 呼び出しがタイムアウトしました (600s)")

    if result.returncode != 0:
        raise RuntimeError(f"Claude Code CLI エラー: {result.stderr.strip()}")
    return result.stdout.strip()


def load_prompt(name):
    """`prompts/<name>.md` を読み込み、frontmatter (--- ... ---) を除去して本文を返す"""
    path = PROMPTS_DIR / f"{name}.md"
    text = path.read_text(encoding="utf-8")
    if text.lstrip().startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            text = parts[2]
    return text.strip()


def extract_section(text, heading):
    """レスポンステキストから特定の見出し以降のテキストを抽出する"""
    keyword = heading.lstrip('#').strip().lstrip('*').rstrip('*').strip()
    lines = text.split('\n')
    for i, line in enumerate(lines):
        stripped = line.strip().lstrip('#').strip().lstrip('*').rstrip('*').strip()
        if stripped == keyword or keyword in stripped:
            return '\n'.join(lines[i + 1:]).strip()
    return ""


# ════════════════════════════════
#  gh / git CLI ヘルパー
# ════════════════════════════════

def _run(cmd, check=True, input_text=None):
    result = subprocess.run(
        cmd,
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=str(PROJECT_ROOT),
    )
    if check and result.returncode != 0:
        raise RuntimeError(f"コマンド失敗: {' '.join(cmd)}\nstderr: {result.stderr.strip()}")
    return result


def _gh(*args, check=True, input_text=None):
    return _run(["gh", *args], check=check, input_text=input_text).stdout.strip()


def _git(*args, check=True):
    return _run(["git", *args], check=check).stdout.strip()


def gh_authenticated():
    return _run(["gh", "auth", "status"], check=False).returncode == 0


def get_default_branch():
    try:
        return _gh("repo", "view", "--json", "defaultBranchRef", "-q", ".defaultBranchRef.name")
    except RuntimeError:
        return "main"


def get_repo_nwo():
    try:
        info = _gh("repo", "view", "--json", "nameWithOwner")
        return json.loads(info).get("nameWithOwner", "")
    except RuntimeError:
        return ""


# ════════════════════════════════
#  ドキュメントテンプレート
# ════════════════════════════════

def make_spec_doc(content, now):
    return (
        f"# 仕様書\n\n"
        f"> 最終更新: {now}\n"
        f"> 生成ツール: SpecFlow（仕様駆動開発アシスタント / Claude Code 内完結版）\n\n"
        f"---\n\n{content}\n"
    )


def make_diagram_doc(mermaid_code, now):
    return (
        f"# シーケンス図\n\n"
        f"> 最終更新: {now}\n"
        f"> 生成ツール: SpecFlow（仕様駆動開発アシスタント / Claude Code 内完結版）\n\n"
        f"---\n\n```mermaid\n{mermaid_code}\n```\n"
    )


# ════════════════════════════════
#  Flask ルート
# ════════════════════════════════

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/detect_ambiguity", methods=["POST"])
def detect_ambiguity():
    requirements = request.get_json().get("requirements", "")
    if not requirements:
        return jsonify({"error": "要件定義書が空です"}), 400
    try:
        reply = call_claude(
            f"以下の要件定義書を分析し、曖昧性を検出して形式的定義で補完してください。\n\n【要件定義書】\n{requirements}",
            system_prompt=load_prompt("ambiguity"),
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({
        "report": reply,
        "enhanced": extract_section(reply, "### 補完済み要件定義書"),
    })


@app.route("/review", methods=["POST"])
def review():
    requirements = request.get_json().get("requirements", "")
    if not requirements:
        return jsonify({"error": "要件定義書が空です"}), 400
    try:
        reply = call_claude(
            f"以下の要件定義書を4本柱（明確性→完全性→一貫性→実装可能性）の順序で厳密にレビューしてください。順序を変えてはいけません。\n\n{requirements}",
            system_prompt=load_prompt("four-pillars"),
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({
        "review": reply,
        "improved": extract_section(reply, "## 改善済み仕様書"),
    })


@app.route("/generate", methods=["POST"])
def generate():
    requirements = request.get_json().get("requirements", "")
    if not requirements:
        return jsonify({"error": "要件定義書が空です"}), 400
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    system_prompt = load_prompt("sequence") + f"\n\n生成日時のプレースホルダは {now} に置換してください。"
    try:
        reply = call_claude(
            f"以下の要件定義書からシーケンス図を生成してください。\n\n{requirements}",
            system_prompt=system_prompt,
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"reply": reply})


@app.route("/refine", methods=["POST"])
def refine():
    data = request.get_json()
    current_code = data.get("current_code", "")
    request_text = data.get("request", "")
    history = data.get("history", [])
    if not current_code or not request_text:
        return jsonify({"error": "パラメータが不足しています"}), 400
    try:
        reply = call_claude(
            f"現在のシーケンス図：\n```mermaid\n{current_code}\n```\n\n修正依頼：{request_text}",
            system_prompt=load_prompt("refine"),
            history=history,
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"reply": reply})


@app.route("/save_to_github", methods=["POST"])
def save_to_github():
    if not gh_authenticated():
        return jsonify({"error": "gh CLI が未認証です。`gh auth login` を実行してください。"}), 400

    data = request.get_json()
    specification = data.get("specification", "")
    mermaid_code = data.get("mermaid_code", "")
    commit_message = data.get("commit_message", "仕様を更新")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    repo = get_repo_nwo()
    if not repo:
        return jsonify({"error": "GitHub リポジトリ情報を取得できません。`gh repo view` が動作するディレクトリで起動してください。"}), 400

    default_branch = get_default_branch()
    try:
        _git("checkout", default_branch)
    except RuntimeError as e:
        return jsonify({"error": f"ブランチ切替失敗: {e}"}), 500

    DOCS_DIR.mkdir(exist_ok=True)
    files = []
    if specification:
        (DOCS_DIR / "specification.md").write_text(make_spec_doc(specification, now), encoding="utf-8")
        files.append("docs/specification.md")
    if mermaid_code:
        (DOCS_DIR / "sequence.md").write_text(make_diagram_doc(mermaid_code, now), encoding="utf-8")
        files.append("docs/sequence.md")
    if not files:
        return jsonify({"error": "保存する内容がありません"}), 400

    try:
        _git("add", *files)
        _git("commit", "-m", f"docs: {commit_message} — 仕様/図を更新 ({now})")
        _git("push", "origin", default_branch)
    except RuntimeError as e:
        return jsonify({"error": f"git 操作失敗: {e}"}), 500

    return jsonify({
        "success": True,
        "message": f"GitHubに保存しました ({now})",
        "url": f"https://github.com/{repo}",
    })


@app.route("/create_pull_request", methods=["POST"])
def create_pr():
    if not gh_authenticated():
        return jsonify({"error": "gh CLI が未認証です。`gh auth login` を実行してください。"}), 400

    data = request.get_json()
    specification = data.get("specification", "")
    mermaid_code = data.get("mermaid_code", "")
    pr_title = data.get("pr_title", "仕様の更新")
    pr_body_text = data.get("pr_body", "")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    branch_name = f"spec-update-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    default_branch = get_default_branch()
    try:
        _git("checkout", default_branch)
        _git("pull", "origin", default_branch)
        _git("checkout", "-b", branch_name)
    except RuntimeError as e:
        return jsonify({"error": f"ブランチ準備失敗: {e}"}), 500

    DOCS_DIR.mkdir(exist_ok=True)
    files = []
    if specification:
        (DOCS_DIR / "specification.md").write_text(make_spec_doc(specification, now), encoding="utf-8")
        files.append("docs/specification.md")
    if mermaid_code:
        (DOCS_DIR / "sequence.md").write_text(make_diagram_doc(mermaid_code, now), encoding="utf-8")
        files.append("docs/sequence.md")
    if not files:
        return jsonify({"error": "保存する内容がありません"}), 400

    try:
        _git("add", *files)
        _git("commit", "-m", f"docs: 仕様/図を更新 ({now})")
        _git("push", "-u", "origin", branch_name)
    except RuntimeError as e:
        return jsonify({"error": f"git 操作失敗: {e}"}), 500

    try:
        ai_pr_body = _generate_pr_body(pr_body_text, specification, now)
    except RuntimeError:
        ai_pr_body = pr_body_text or "仕様を更新しました。"

    try:
        pr_url = _gh(
            "pr", "create",
            "--title", pr_title,
            "--body", ai_pr_body,
            "--base", default_branch,
            "--head", branch_name,
        )
    except RuntimeError as e:
        return jsonify({"error": f"PR 作成失敗: {e}"}), 500

    return jsonify({
        "success": True,
        "pr_url": pr_url,
        "branch": branch_name,
        "message": "Pull Requestを作成しました",
    })


@app.route("/detect_diff", methods=["POST"])
def detect_diff():
    if not gh_authenticated():
        return jsonify({"error": "gh CLI が未認証です。"}), 400

    current_spec = request.get_json().get("current_spec", "")
    if not current_spec:
        return jsonify({"error": "現在の仕様が空です"}), 400

    default_branch = get_default_branch()
    previous_spec = _run(
        ["git", "show", f"{default_branch}:docs/specification.md"], check=False
    ).stdout

    if not previous_spec.strip():
        return jsonify({
            "has_previous": False,
            "message": "GitHubにまだ仕様書が保存されていません。初回の保存になります。",
        })

    if previous_spec.strip() == current_spec.strip():
        return jsonify({
            "has_previous": True,
            "no_change": True,
            "message": "前回の保存から変更はありません。",
        })

    try:
        diff_report = call_claude(
            f"【前回の仕様書】\n{previous_spec}\n\n【現在の仕様書】\n{current_spec}",
            system_prompt=load_prompt("diff"),
        )
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "has_previous": True,
        "no_change": False,
        "diff_report": diff_report,
    })


def _generate_pr_body(user_description, specification, now):
    prompt = f"""以下の情報を元に、GitHubのPull Request説明文を日本語で作成してください。
仕様駆動開発の観点から、変更の意図・内容・影響範囲を明確に記述してください。

【変更の概要】
{user_description or "仕様の更新"}

【更新された仕様書の内容（抜粋）】
{specification[:500] if specification else "（なし）"}

【出力フォーマット】
## 変更の概要
## 変更理由（Why）
## 変更内容（What）
## 影響範囲
## レビューのポイント
## AI利用の記録
- AI生成ツール: SpecFlow (Claude Code Skills)
- 生成日時: {now}
- Human in the Loop: レビュー・承認は人間が実施"""
    return call_claude(prompt)


if __name__ == "__main__":
    app.run(debug=True)
