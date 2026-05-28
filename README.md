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
| 補完スタイル | 形式的定義（集合論・述語論理） | **自然言語**（Why/Whatに集中、Howは記述しない） |
| AI判断の透明性 | なし | **判断根拠ログ**を毎回出力・蓄積し、Skill改善サイクルに活用 |

外部 API キーの管理が不要になり、すべての AI ロジックは Skill としても Slash command として直接呼べる。

---

## 設計思想

### 透明性（Transparency）

AIが「なぜそう判断したか」を毎回出力する。

- **根拠種別**: 仕様内の記述か、AIの暗黙知（一般知識・設計慣習）かを明示
- **暗黙知追記サマリ**: 仕様に書かれていないのにAIが追加した内容を一覧化
- **評価方針宣言**: 4本柱の各柱を評価する前に、どう解釈しどの順序で確認するかを宣言

これによりAIの判断を人間が検証・修正できる。

### Skill改善サイクル（Skill Evolution）

```
パイプライン実行
    ↓ AIの判断根拠が docs/ai-decision-log.md に自動蓄積
複数回実行後
    ↓ /refine-skills-from-log でパターン分析
繰り返し使われた暗黙知 → SKILL.md に明示ルールとして追記
    ↓ skill-creator で構造最適化
再現性の高い Skill へ
```

---

## システム構成

```
claude_speckflow_sequence/
├── README.md
├── app.py                                 # Flask UI（外部 API 非依存）
├── templates/
│   └── index.html
├── docs/
│   ├── specification.md                   # 仕様書（パイプラインが自動更新）
│   ├── sequence.md                        # シーケンス図（パイプラインが自動更新）
│   └── ai-decision-log.md                 # AI意思決定ログ（各Skillが自動追記）
├── prompts/                               # 再利用可能なシステムプロンプト
│   ├── ambiguity.md
│   ├── four-pillars.md                    # 4本柱レビュー方法論
│   ├── sequence.md
│   ├── refine.md
│   └── diff.md
├── examples/
│   └── sample-requirements.txt
└── .claude/
    └── skills/                            # Claude Code Skill 群
        ├── detect-ambiguity/SKILL.md      # 曖昧性検出（自然言語補完）
        ├── review-spec/SKILL.md           # 4本柱レビュー統合実行
        ├── four-pillars-review/SKILL.md   # 評価順序・方法論本体
        ├── generate-sequence/SKILL.md     # Mermaidシーケンス図生成
        ├── refine-sequence/SKILL.md       # 既存図の対話的修正
        ├── save-spec-git/SKILL.md         # mainへ直接コミット
        ├── create-spec-pr/SKILL.md        # PR作成
        ├── detect-spec-diff/SKILL.md      # 前回との差分検出
        ├── specflow-pipeline/SKILL.md     # 全工程オーケストレータ
        ├── refine-skills-from-log/SKILL.md # ログ分析→Skill改善案生成
        ├── generate-class-diagram/SKILL.md
        ├── generate-er-diagram/SKILL.md
        ├── generate-flowchart/SKILL.md
        └── generate-specflow-system/SKILL.md
```

---

## Skills 一覧

### SpecFlow 中核

| Skill | 役割 | 旧エンドポイント |
|-------|------|------------------|
| `detect-ambiguity` | 要件の曖昧性検出 + 自然言語補完 | `/detect_ambiguity` |
| `review-spec` | 4本柱レビュー統合実行 | `/review` |
| `four-pillars-review` | **4本柱の評価順序・方法論本体**（独立Skill） | — |
| `generate-sequence` | Mermaid シーケンス図生成 | `/generate` |
| `refine-sequence` | 既存図の対話的修正 | `/refine` |
| `detect-spec-diff` | 前回保存との差分解説 | `/detect_diff` |
| `save-spec-git` | デフォルトブランチに直接コミット | `/save_to_github` |
| `create-spec-pr` | 新ブランチを切って PR 作成 | `/create_pull_request` |

### Skill改善サイクル

| Skill | 役割 |
|-------|------|
| `specflow-pipeline` | 曖昧性検出 → レビュー → 図生成 → 差分 → 保存/PR を通しで実行。完了後に `/refine-skills-from-log` を案内 |
| `refine-skills-from-log` | `docs/ai-decision-log.md` のパターンを分析し、SKILL.md改善案を生成。skill-creator への引き渡しサマリも出力 |

### Mermaid 汎用（拡張）

| Skill | 用途 |
|-------|------|
| `generate-class-diagram` | クラス図・ドメインモデル |
| `generate-er-diagram` | ER 図・データモデル |
| `generate-flowchart` | フローチャート・状態遷移 |

---

## 4本柱レビュー方法論

`review-spec` が呼ぶ評価順序は **固定** で、入れ替え禁止：

```
明確性 (Clarity)         ← 曖昧な文では後段の判定が成立しない
   ↓
完全性 (Completeness)    ← 明確でなければ「抜け」を判定できない
   ↓
一貫性 (Consistency)     ← 完全に揃って初めて矛盾比較ができる
   ↓
実装可能性 (Feasibility) ← 上3つを満たした要件を現実制約で最終ゲート
```

各柱の具体的なチェック項目は
[four-pillars-review Skill](.claude/skills/four-pillars-review/SKILL.md) と
[prompts/four-pillars.md](prompts/four-pillars.md) に明文化されている。

---

## セットアップ

### 1. 依存ライブラリ

```bash
pip install flask
```

> 旧版で必要だった `anthropic` と `python-dotenv` は **不要**。

### 2. Claude Code CLI

```bash
# https://docs.claude.com/claude-code に従ってインストール
claude --version
```

### 3. GitHub CLI

```bash
gh auth login
gh auth status   # ← 成功すること
```

### 4. skill-creator のインストール（任意・Skill改善に使用）

Claude Code 上で実行：

```
/plugin marketplace add anthropics/skills
/plugin install example-skills@anthropic-agent-skills
```

または手動：

```bash
git clone https://github.com/anthropics/skills.git
mkdir -p ~/.claude/skills
cp -r skills/skills/skill-creator ~/.claude/skills/
```

---

## 使い方

### 全工程をパイプラインで回す（基本フロー）

```
/specflow-pipeline docs/specification.md
```

各ステップでAIの判断根拠が提示される。確認・承認しながら進む。

| ステップ | 内容 |
|---------|------|
| 1. detect-ambiguity | 曖昧箇所を検出。なぜ曖昧と判断したか・使用した暗黙知を出力 |
| 2. review-spec | 4本柱でレビュー。各柱の評価前に方針宣言、評価後に根拠ログを出力 |
| 3. generate-sequence | シーケンス図を生成。設計判断の根拠を出力 |
| 4. detect-spec-diff | 前回との差分を確認 |
| 5. 保存 | main直接コミット or PR作成を選択 |

→ 実行のたびに `docs/ai-decision-log.md` へAIの判断が自動追記される。

### 個別 Skill を使う

```
/detect-ambiguity   docs/specification.md
/review-spec        docs/specification.md
/generate-sequence  docs/specification.md
/refine-sequence    "予約フローにタイムアウト処理を追加して"
/detect-spec-diff
/save-spec-git
/create-spec-pr
```

### Skill を育てる（複数回実行後）

```
/refine-skills-from-log
```

`docs/ai-decision-log.md` のパターンを分析し、「毎回同じ暗黙知が使われている」箇所を
明示ルールとしてSKILL.mdへの追記案を生成する。

採用した改善案は skill-creator で構造最適化できる：

```
skill-creatorを使って、このSKILL.mdのdescriptionと構造を最適化して
```

---

## AI意思決定ログ（docs/ai-decision-log.md）

パイプライン実行のたびに以下が記録される：

| 記録内容 | 目的 |
|---------|------|
| 曖昧と判断した理由・根拠種別 | なぜその箇所が問題か人間が確認できる |
| 4本柱の評価方針と優先順位 | AIがどの順序でどの基準で評価したか |
| 暗黙知追記サマリ | 仕様に書かれていないのに追加した内容の一覧 |
| 設計判断ログ（シーケンス図） | 参加者・フロー・エラーパスの選択根拠 |

ログが蓄積されると `/refine-skills-from-log` でパターン分析が可能になる。

---

## なぜ Claude Code 内で完結させたか

1. **API キー管理から解放** — `.env` 漏洩リスクが消える
2. **Skill 単位で再利用** — 「曖昧性検出だけ」「4本柱だけ」を他の文脈でも呼べる
3. **AIの判断が検証可能** — 透明性出力により、AIが何をどう考えたかが追跡できる
4. **Skill が育つ** — ログ→パターン分析→SKILL.md改善→再現性向上のサイクルが回る

---

## 研究背景

学部卒業研究「対象ドメイン定義に数学構造を含めて LLM に注入することによる推論性能の向上と検証」(2025)
の知見を踏まえ、本版では **形式的記法（集合論・述語論理）を仕様書から除外** し、
仕様駆動開発の原則「Why/Whatを記述しHowは記述しない」に従った自然言語仕様に統一している。

AIの暗黙知を透明化し、人間が確認・修正しながらSkillを育てることで、
**何度実行しても同じ品質の出力が得られる再現性** を目指す。

---

## ライセンス・出典

- 原版: [MahiroIkeda/sequence-chatbot_2](https://github.com/MahiroIkeda/sequence-chatbot_2)
- 本版: 同上を Claude Code 内完結に再設計
