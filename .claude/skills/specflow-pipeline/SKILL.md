---
name: specflow-pipeline
description: Run the full SpecFlow pipeline end-to-end — ambiguity detection → 4-pillar review → sequence diagram generation → diff against last saved → save or PR. Use when the user provides a requirements document and wants the complete spec-driven workflow executed in one go. This is the orchestrator skill that calls the other SpecFlow skills in order.
---

# specflow-pipeline

SpecFlow全工程をワンショットで実行するオーケストレータSkill。

## いつ使うか

- ユーザーが要件定義書を渡して「全部やって」「パイプライン回して」と依頼したとき
- レビュー〜PRまでを通しで実行したいとき

## 実行順序

```
1. detect-ambiguity        → 補完済み仕様
2. review-spec             → 4本柱レビュー + 改善済み仕様 (=最終仕様)
3. generate-sequence       → Mermaidシーケンス図
4. detect-spec-diff        → 前回保存との差分
5. save-spec-git OR
   create-spec-pr          → GitHub反映（ユーザーに選択させる）
```

各ステップで内部的に対応Skillを呼び出す：
- `[[detect-ambiguity]]`
- `[[review-spec]]` (内部で `[[four-pillars-review]]` を使用)
- `[[generate-sequence]]`
- `[[detect-spec-diff]]`
- `[[save-spec-git]]` または `[[create-spec-pr]]`

## 進行ルール

- 各ステップ完了時にユーザーへ要約を提示し、次に進む承認を得る（Human in the Loop）
- 致命的な問題が出た場合（例: 柱4で「実装不可能」判定）はパイプラインを停止し、原因を提示する
- 最終ステップだけは「save」か「PR」かを必ずユーザーに選ばせる

## 出力ファイル配置

- `docs/specification.md` — 最終仕様
- `docs/sequence.md` — 最終シーケンス図
- `docs/ambiguity-report.md` — 曖昧性レポート（任意）
- `docs/review-report.md` — レビューレポート（任意）

## 関連Skill

すべてのSpecFlow関連Skillを参照する：
- `[[detect-ambiguity]]`, `[[review-spec]]`, `[[four-pillars-review]]`
- `[[generate-sequence]]`, `[[refine-sequence]]`
- `[[detect-spec-diff]]`, `[[save-spec-git]]`, `[[create-spec-pr]]`
