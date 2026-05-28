# SpecFlow — 仕様駆動開発アシスタント (Claude Code 内完結版)

要件定義書からシーケンス図を自動生成し、GitHubと連携して仕様とコードを同期管理する。
本リポジトリは [MahiroIkeda/sequence-chatbot_2](https://github.com/MahiroIkeda/sequence-chatbot_2) を
**Claude Code 内で完結する形に再設計** した版である。

---

## 旧版との違い

| 観点 | 旧版 | 本版 |
|------|------|------|
| AI 推論 | Anthropic API への直接呼び出し（`anthropic` SDK） | **Claude Code CLI** を `subprocess` で呼ぶ（`claude -p`） |
| GitHub 連携 | GitHub REST API への直接呼び出し（`urllib`） | **`gh` CLI** + `git` コマンドを `subprocess` で呼ぶ |
| 認証情報 | `.env` に `ANTHROPIC_API_KEY` + `GITHUB_TOKEN` | **不要**（Claude Code と `gh` の既存セッションを使用） |
| 利用方法 | Flask Web UI のみ | Flask UI + Claude Code **Skills**（`/specflow-pipeline` 等）の併用 |
| Cowork 対応 | 無し | `.claude/skills/` 配下に Skill 群を配置（Cowork から呼び出し可能） |

外部 API キーの管理が不要になり、すべての AI ロジックは Skill としても Slash command として直接呼べる。

---

## システム構成

```
claude_code_chatbot/
├── README.md
├── app.py                                 # Flask UI（外部 API 非依存）
├── templates/
│   └── index.html                         # 旧版と同一の Web UI
├── docs/
│   ├── SPEC_DRIVEN.md                     # 仕様駆動開発の理論
│   ├── specification.md                   # 仕様書（自動更新）
│   └── sequence.md                        # シーケンス図（自動更新）
├── prompts/                               # 再利用可能なシステムプロンプト
│   ├── ambiguity.md
│   ├── four-pillars.md                    # 4本柱レビュー方法論
│   ├── sequence.md
│   ├── refine.md
│   └── diff.md
├── examples/
│   └── sample-requirements.txt
└── .claude/
    ├── settings.json
    └── skills/                            # Claude Code / Cowork から呼べる Skill 群
        ├── detect-ambiguity/SKILL.md
        ├── review-spec/SKILL.md
        ├── four-pillars-review/SKILL.md   # 評価順序・方法論本体
        ├── generate-sequence/SKILL.md
        ├── refine-sequence/SKILL.md
        ├── save-spec-git/SKILL.md
        ├── create-spec-pr/SKILL.md
        ├── detect-spec-diff/SKILL.md
        ├── generate-class-diagram/SKILL.md
        ├── generate-er-diagram/SKILL.md
        ├── generate-flowchart/SKILL.md
        ├── specflow-pipeline/SKILL.md     # 全工程オーケストレータ
        └── generate-specflow-system/SKILL.md  # メタ Skill：別プロジェクトに同型システムを構築
```

---

## Skills 一覧

### SpecFlow 中核（旧 Flask エンドポイントに対応）

| Skill | 役割 | 旧エンドポイント |
|-------|------|------------------|
| `detect-ambiguity` | 要件の曖昧性検出 + 形式的補完 | `/detect_ambiguity` |
| `review-spec` | 4本柱レビュー統合実行 | `/review` |
| `four-pillars-review` | **4本柱の評価順序・方法論本体**（独立Skill） | — |
| `generate-sequence` | Mermaid シーケンス図生成 | `/generate` |
| `refine-sequence` | 既存図の対話的修正 | `/refine` |
| `detect-spec-diff` | 前回保存との差分解説 | `/detect_diff` |
| `save-spec-git` | デフォルトブランチに直接コミット | `/save_to_github` |
| `create-spec-pr` | 新ブランチを切って PR 作成 | `/create_pull_request` |

### Mermaid 汎用（拡張）

| Skill | 用途 |
|-------|------|
| `generate-class-diagram` | クラス図・ドメインモデル |
| `generate-er-diagram` | ER 図・データモデル |
| `generate-flowchart` | フローチャート・状態遷移 |

### メタ Skill

| Skill | 用途 |
|-------|------|
| `specflow-pipeline` | 曖昧性検出 → レビュー → 図生成 → 差分 → 保存/PR を通しで実行 |
| `generate-specflow-system` | **別プロジェクトに同型システムを Scaffold** |

---

## 4本柱レビュー方法論

`review-spec` が呼ぶ評価順序は **固定** で、入れ替え禁止：

```
明確性 (Clarity)   ← 曖昧な文では後段の判定が成立しない
   ↓
完全性 (Completeness)   ← 明確でなければ「抜け」を判定できない
   ↓
一貫性 (Consistency)   ← 完全に揃って初めて矛盾比較ができる
   ↓
実装可能性 (Feasibility)   ← 上3つを満たした要件を現実制約で最終ゲート
```

各柱の具体的なチェック項目・なぜこの順序なのかは
[four-pillars-review Skill](.claude/skills/four-pillars-review/SKILL.md) と
[prompts/four-pillars.md](prompts/four-pillars.md) に明文化されている。

単一柱モード（例: 「明確性だけチェック」）も可能だが、その柱が前提とする上位柱が満たされない可能性を必ず警告する。

---

## セットアップ

### 1. 依存ライブラリ

```bash
pip install flask
```

> 旧版で必要だった `anthropic` と `python-dotenv` は **不要** になった。

### 2. Claude Code CLI

```bash
# https://docs.claude.com/claude-code に従ってインストール
claude --version
```

### 3. GitHub CLI

```bash
# https://cli.github.com/ からインストール後
gh auth login
gh auth status   # ← 成功すること
```

### 4. 起動

#### A) Flask UI 経由（旧版と同じ体験）

```bash
python app.py
# → http://localhost:5000
```

#### B) Claude Code Skill 経由（推奨・Cowork 互換）

```bash
claude
# 起動後
/specflow-pipeline                # 全工程
/detect-ambiguity <要件ファイル>  # 単発
/four-pillars-review              # 評価方法論の説明
```

---

## 使い方（典型フロー）

### 全工程をパイプラインで回す

```
/specflow-pipeline examples/sample-requirements.txt
```

→ 曖昧性検出 → 4本柱レビュー → シーケンス図 → 差分 → 保存/PR の各ステップで確認しながら進む。

### 個別 Skill を使う

```
/detect-ambiguity   path/to/requirements.txt
/review-spec        docs/specification.md
/generate-sequence  docs/specification.md
/refine-sequence    "予約フローにタイムアウト処理を追加して"
/detect-spec-diff
/save-spec-git
/create-spec-pr     "予約機能を追加"
```

### Flask UI から使う

旧版の UI が `templates/index.html` にそのまま残っており、ボタン操作の体感は同じ。
バックエンドが Claude Code CLI と `gh` CLI を呼ぶように差し替えられている。

---

## 別プロジェクトに同型システムを入れる（Cowork 用途）

Cowork で同僚が「うちのリポジトリにも SpecFlow を入れたい」と頼んできたら：

```
/generate-specflow-system
```

を呼ぶと、対象ディレクトリに `.claude/skills/`, `prompts/`, `templates/`, `app.py`, `docs/SPEC_DRIVEN.md` 一式が
コピーされる。`gh auth status` まで自動チェックされる。

詳細は [generate-specflow-system Skill](.claude/skills/generate-specflow-system/SKILL.md) を参照。

---

## なぜ Claude Code 内で完結させたか

1. **API キー管理から解放** — `.env` 漏洩リスクが消える
2. **Cowork 親和性** — Skill 化したので同僚と即座に共有できる
3. **Skill 単位で再利用** — 「曖昧性検出だけ」「4本柱だけ」を他の文脈でも呼べる
4. **コスト透明性** — Claude Code のセッション単位で消費を観察できる

---

## 研究背景

学部卒業研究「対象ドメイン定義に数学構造を含めて LLM に注入することによる推論性能の向上と検証」(2025)
の知見を実装に組み込み、曖昧性を形式的補完してからシーケンス図を生成する設計としている。
本版はさらに **Skill 化** することで、Claude Code / Cowork における仕様駆動開発の
再利用可能な基盤を目指す。

---

## ライセンス・出典

- 原版: [MahiroIkeda/sequence-chatbot_2](https://github.com/MahiroIkeda/sequence-chatbot_2)
- 本版: 同上を Claude Code 内完結に再設計
