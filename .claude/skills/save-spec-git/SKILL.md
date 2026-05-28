---
name: save-spec-git
description: Save the specification document and sequence diagram directly to a GitHub repository's default branch using the `gh` CLI (no REST API token plumbing required). Use when the user wants to commit/push the current spec+diagram to GitHub. Replaces the original Flask /save_to_github endpoint with a Claude Code-native workflow using gh CLI.
---

# save-spec-git

`docs/specification.md` と `docs/sequence.md` を GitHub のデフォルトブランチに直接コミットするSkill。

旧 `app.py` の `/save_to_github` を `gh` CLI ベースに置換したもの。Anthropic API も GitHub REST API も使わない。

## 前提

- `gh` CLI がインストール・認証済み (`gh auth status` でOK)
- カレントリポジトリで `gh repo view` が成功すること
- Git作業ツリーがクリーンであること（または、stageされた変更がコミット対象であることをユーザー確認済み）

## 入力

- `specification` — 仕様書本文（省略可。省略時は既存の `docs/specification.md` を使う）
- `mermaid_code` — Mermaidコード（省略可）
- `commit_message` — コミットメッセージ（デフォルト: "仕様を更新"）

## 手順

1. `gh auth status` で認証を確認。失敗時はユーザーに `gh auth login` を指示
2. リポジトリ情報を取得：`gh repo view --json defaultBranchRef,nameWithOwner`
3. 現在のブランチがデフォルトブランチか確認。違えば `git checkout <default>` を確認した上で実施
4. 仕様書テンプレートで `docs/specification.md` を生成・上書き：
   ```
   # 仕様書

   > 最終更新: <YYYY-MM-DD HH:MM>
   > 生成ツール: SpecFlow（仕様駆動開発アシスタント）

   ---

   <specification 本文>
   ```
5. 図テンプレートで `docs/sequence.md` を生成・上書き：
   ```
   # シーケンス図

   > 最終更新: <YYYY-MM-DD HH:MM>
   > 生成ツール: SpecFlow（仕様駆動開発アシスタント）

   ---

   ```mermaid
   <mermaid_code>
   ```
   ```
6. `git add docs/specification.md docs/sequence.md`
7. `git commit -m "docs: <commit_message> — 仕様/図を更新 (<日時>)"`
8. `git push` でデフォルトブランチへpush

## エラー処理

- 認証失敗 → ユーザーに `gh auth login` を促す
- リモートが存在しない → ユーザーに `gh repo create` を提案
- pushが拒否された → `git pull --rebase` を確認

## なぜREST APIを使わないか

`gh` CLI は内部でGitHub APIを呼ぶが、Claude Code はそれを **トークンを直接扱わずに** 実行できる。
これにより `.env` の `GITHUB_TOKEN` 管理が不要になり、認証はOSの `gh` セッションに委譲される。

## 関連Skill

- `[[create-spec-pr]]` — デフォルトブランチではなくPRで反映したい場合
- `[[detect-spec-diff]]` — 保存前の差分検出
