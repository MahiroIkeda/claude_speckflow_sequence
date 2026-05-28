---
name: generate-specflow-system
description: Scaffold a brand-new SpecFlow-style spec-driven development system inside any project directory — sets up .claude/skills, prompts/, docs/, templates/, app.py (no external APIs), and a minimal Flask UI. Use when the user wants to bootstrap SpecFlow capabilities in a NEW repository (not the current one). The generated system uses Claude Code skills for all AI work and `gh` CLI for GitHub work — no Anthropic API key or GITHUB_TOKEN required.
---

# generate-specflow-system

新規プロジェクトに SpecFlow 型システムを自動構築するメタSkill。
Claude Cowork で「うちのリポジトリにも SpecFlow を入れたい」と頼まれたときに使う。

## 生成物

```
<target>/
├── README.md
├── app.py                   # Flask UI（外部API不使用）
├── templates/index.html
├── docs/
│   ├── SPEC_DRIVEN.md
│   ├── specification.md
│   └── sequence.md
├── prompts/
│   ├── ambiguity.md
│   ├── four-pillars.md
│   ├── sequence.md
│   ├── refine.md
│   └── diff.md
├── examples/
│   └── sample-requirements.txt
└── .claude/skills/
    ├── detect-ambiguity/SKILL.md
    ├── review-spec/SKILL.md
    ├── four-pillars-review/SKILL.md
    ├── generate-sequence/SKILL.md
    ├── refine-sequence/SKILL.md
    ├── save-spec-git/SKILL.md
    ├── create-spec-pr/SKILL.md
    ├── detect-spec-diff/SKILL.md
    ├── generate-class-diagram/SKILL.md
    ├── generate-er-diagram/SKILL.md
    ├── generate-flowchart/SKILL.md
    └── specflow-pipeline/SKILL.md
```

## 手順

1. ユーザーに対象ディレクトリを確認（デフォルト: カレント）
2. ディレクトリの既存ファイルと衝突しないかチェック
   - 衝突する場合は上書きするか別パス（例: `.claude/skills/specflow/`）に隔離するか確認
3. 上記ツリーをコピー：
   - このリポジトリ（テンプレート元）の `prompts/`, `.claude/skills/`, `templates/`, `app.py`, `docs/SPEC_DRIVEN.md` をコピー
   - `docs/specification.md` と `docs/sequence.md` は空テンプレで生成
4. ターゲットの README に「SpecFlow導入済み」セクションを追記
5. ターゲットが git リポジトリでなければ `git init` を提案
6. `gh auth status` を実行し未認証なら `gh auth login` を案内
7. 動作確認：
   - `python app.py` 起動
   - http://localhost:5000 アクセス
   - もしくは Claude Code から `/specflow-pipeline` を直接呼んでテスト

## カスタマイズ可能ポイント

ユーザー要求に応じて以下を調整：

- **4本柱の重み調整** — 例: スタートアップ向けは実装可能性を最優先にする等
- **言語切替** — プロンプトを英語版に差し替え
- **追加図種** — `generate-state-diagram` Skill を追加するなど
- **PR本文テンプレ** — 組織のテンプレに合わせる
- **コミットメッセージ規約** — Conventional Commits 等への適合

## ガード条件

- ターゲットディレクトリが本テンプレート元自身でないか確認（自己上書き防止）
- `git status` がクリーンでないなら警告
- 既存の `.claude/skills/<name>` と衝突する場合は明示的に上書き承認を得る

## 関連Skill

- `[[specflow-pipeline]]` — 生成後、最初に呼ばれる想定の入口Skill
- このリポジトリ自身がリファレンス実装
