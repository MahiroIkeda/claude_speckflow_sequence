---
name: detect-spec-diff
description: Compare the current in-memory specification with the last-saved version on GitHub (default branch) and produce a Japanese diff analysis report — added/removed/changed requirements, impact analysis, recommended next actions. Use before saving or creating a PR to summarize what has changed. Replaces the original /detect_diff endpoint.
---

# detect-spec-diff

現在の仕様と GitHub 上の保存済み仕様の差分をAI解説するSkill。
旧 `/detect_diff` を `gh` CLI ベースで再実装。

## 入力

- `current_spec` — 現在の仕様書本文

## 手順

1. GitHub上の `docs/specification.md` の内容を取得：
   ```
   gh api repos/{owner}/{repo}/contents/docs/specification.md --jq .content | base64 -d
   ```
   またはローカルリポジトリ内なら `git show <default>:docs/specification.md`
2. ファイルが存在しない場合 → `{has_previous: false, message: "初回保存になります"}` を返す
3. 内容が同一なら → `{no_change: true, message: "前回保存から変更なし"}` を返す
4. 差分がある場合、[prompts/diff.md](../../../prompts/diff.md) をシステムプロンプトとして使い、以下を生成：
   - 変更サマリー
   - 追加された要件
   - 削除された要件
   - 変更された要件（前後対照）
   - 影響範囲の分析
   - 推奨アクション
5. 結果をユーザーに表示。`[[create-spec-pr]]` 経由で呼ばれた場合はPR本文に再利用

## 補助: ローカル git diff の活用

ローカルリポジトリ内なら `git diff HEAD -- docs/specification.md` を併用して、
正確な行レベル差分も提示できる。AI解説はその意味的差分の補強として使う。

## 関連Skill

- `[[save-spec-git]]` — 差分確認後の保存
- `[[create-spec-pr]]` — PR本文に差分を流用
