---
name: review-spec
description: Review a specification document using the 4-pillar methodology (Clarity → Completeness → Consistency → Feasibility) in strict order. Use when the user asks to "review", "evaluate", or "audit" a requirements/specification document, or to get improvement suggestions. Produces a structured Japanese review report and an improved full-text specification.
---

# review-spec

仕様書を4本柱（明確性・完全性・一貫性・実装可能性）でレビューするSkill。
詳細な評価順序・依存関係は `[[four-pillars-review]]` Skill に従う。

## いつ使うか

- ユーザーが「レビューして」「改善提案して」と仕様書をレビュー依頼したとき
- `/specflow-pipeline` の第2ステップ（曖昧性検出後）として呼ばれたとき
- PR作成前の品質ゲートとして

## 手順

1. レビュー対象の仕様書（パス or 本文）を取得する
2. [prompts/four-pillars.md](../../../prompts/four-pillars.md) と [`[[four-pillars-review]]`](../four-pillars-review/SKILL.md) の方法論に従い、**順序を厳守** して評価する：
   - 柱1: 明確性 → 完了するまで柱2に進まない
   - 柱2: 完全性 → 完了するまで柱3に進まない
   - 柱3: 一貫性 → 完了するまで柱4に進まない
   - 柱4: 実装可能性
3. 各柱で：
   - チェック項目を機械的に走査
   - 該当箇所を引用して指摘
   - 改善案を提示
4. 統合フォーマットで出力：
   ```
   ## レビュー結果
   ### 1. 明確性
   ### 2. 完全性
   ### 3. 一貫性
   ### 4. 実装可能性
   ## 改善提案
   ## 改善済み仕様書
   ```

## 重要な制約

- 4本柱は **必ずこの順序で** 評価する。順序を入れ替えると前提が崩れる
- 柱1で曖昧性が多数残る場合、まず `[[detect-ambiguity]]` を実行してから戻ってくることを提案する
- 「改善済み仕様書」は省略せず全文を出力する

## 関連Skill

- `[[detect-ambiguity]]` — レビュー前の曖昧性除去
- `[[four-pillars-review]]` — 4本柱方法論の本体
- `[[generate-sequence]]` — レビュー後の図生成
