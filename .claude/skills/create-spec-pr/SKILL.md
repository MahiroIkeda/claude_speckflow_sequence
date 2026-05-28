---
name: create-spec-pr
description: Create a new branch with updated spec+diagram, push it, and open a Pull Request with an AI-generated PR body — all via `gh` CLI. Use when the user wants to propose spec changes via PR (instead of committing directly to main). Replaces the original Flask /create_pull_request endpoint.
---

# create-spec-pr

仕様書・シーケンス図を新ブランチにコミットし、`gh pr create` でPRを開くSkill。
旧 `/create_pull_request` を `gh` CLI ベースに置換。

## 前提

- `gh auth status` 通過
- リポジトリにpush権限があること
- ベースとなるデフォルトブランチが最新であること

## 入力

- `specification`, `mermaid_code` — 保存対象
- `pr_title` — PRタイトル（デフォルト: "仕様の更新"）
- `pr_body` — ユーザーが書いたPR説明文（任意）

## 手順

1. デフォルトブランチ名を取得：`gh repo view --json defaultBranchRef -q .defaultBranchRef.name`
2. デフォルトブランチをチェックアウト＆pull：
   ```
   git checkout <default>
   git pull
   ```
3. 新ブランチを作成：`git checkout -b spec-update-<YYYYMMDD-HHMMSS>`
4. `docs/specification.md` と `docs/sequence.md` を更新（`[[save-spec-git]]` と同じテンプレ）
5. コミット：`git add docs/ && git commit -m "docs: 仕様/図を更新"`
6. push：`git push -u origin spec-update-<...>`
7. **PR本文をAI生成**（Claude Code自身が以下のテンプレートで作成）：
   ```
   ## 変更の概要
   ## 変更理由（Why）
   ## 変更内容（What）
   ## 影響範囲
   ## レビューのポイント
   ## AI利用の記録
   - AI生成ツール: SpecFlow (Claude Code Skills)
   - 生成日時: <YYYY-MM-DD HH:MM>
   - Human in the Loop: レビュー・承認は人間が実施
   ```
   生成材料：ユーザーの `pr_body`、仕様書冒頭500文字、`[[detect-spec-diff]]` の差分レポート
8. PR作成：`gh pr create --title "<pr_title>" --body "<生成本文>" --base <default> --head spec-update-<...>`
9. 出力としてPR URLとPR番号をユーザーに返す

## エラー処理

- pushが拒否された場合 → ベースブランチが進んでいる可能性。`git pull --rebase origin <default>` を案内
- PR作成失敗 → 既存PRが衝突していないか `gh pr list --head <branch>` で確認

## 関連Skill

- `[[save-spec-git]]` — PRを介さず直接push
- `[[detect-spec-diff]]` — PR本文作成の材料として呼ばれる
