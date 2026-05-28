---
name: refine-skills-from-log
description: Analyze the AI decision log at docs/ai-decision-log.md and propose concrete improvements to SKILL.md files. Use when the user wants to review accumulated AI decisions, identify implicit knowledge patterns, and harden those patterns into explicit SKILL.md rules — the input for skill-creator.
---

# refine-skills-from-log

`docs/ai-decision-log.md` に蓄積されたAI意思決定ログを分析し、SKILL.md改善案を生成するSkill。

## いつ使うか

- パイプラインを複数回実行し、ログが蓄積された後
- AIの判断パターンを確認してSKILLを強化したいとき
- skill-creatorへの入力としてSKILL.md改善案が必要なとき

## 手順

1. `docs/ai-decision-log.md` を読み込む
2. 以下の3つの観点でパターンを抽出する：

   **観点A: 繰り返し使われた暗黙知**
   - 複数の実行で同じ暗黙知が登場している → 明示的なルールとしてSKILL.mdに追記すべき

   **観点B: 繰り返し登場した優先順位パターン**
   - 4本柱の評価で同じ優先順位（例：「用語の揺れを最初に確認する」）が繰り返されている → SKILL.mdに固定ルールとして追記すべき

   **観点C: 繰り返し検出された曖昧性の種類**
   - 特定の種別（例：種別6「数量の曖昧さ」）が毎回多く検出される → detect-ambiguityの重点チェック項目として追記すべき

3. 各SKILL.mdへの具体的な改善案を以下の形式で出力する：

```
## SKILL.md改善案

### 対象: detect-ambiguity/SKILL.md
**追記箇所**: ## 検出する曖昧性の種類
**追記内容**:
> ※ ログから観察: 種別6（数量の曖昧さ）は毎回3件以上検出される。特に「〇〇日」「〇〇分以内」などの時間表現を重点的にスキャンすること。
**根拠**: ai-decision-log.md 実行1・実行2・実行3 で同パターン検出

### 対象: four-pillars-review/SKILL.md
**追記箇所**: ### 柱1: 明確性 — チェック項目
**追記内容**:
> ※ ログから観察: このシステムでは「DB制約と業務フローの整合」が毎回一貫性問題として浮上する。柱3の評価開始前に必ず確認すること。
**根拠**: ai-decision-log.md 実行2・実行3 で同パターン

### 対象: generate-sequence/SKILL.md
**追記箇所**: ## Mermaid構文の制約ルール
**追記内容**:
（新たに発見されたパターンがあれば追記）
**根拠**: ...
```

4. 改善案をユーザーに提示し、採用可否を確認する
5. 採用された改善案を実際のSKILL.mdに反映する（Editツール使用）
6. skill-creatorへの引き渡し用サマリを出力する：

```
## skill-creator 引き渡しサマリ

以下のSKILL.mdが改善されました。skill-creatorを使って構造を最適化することを推奨します。

| SKILL.md | 変更内容の概要 | skill-creatorへの指示案 |
|---------|--------------|----------------------|
| detect-ambiguity | 重点チェック項目を追加 | 「このSKILL.mdのdescriptionと手順の簡潔化をお願いします」 |
| four-pillars-review | 柱3の固定ルールを追加 | 「このSKILL.mdのProgressive Disclosure最適化をお願いします」 |
```

## 出力の品質基準

- 改善案は必ずログの具体的な実行回・行を根拠として引用すること
- 「毎回同じ暗黙知が使われた」ことを示すには、**2回以上の実行**でのパターン一致が必要
- 1回しか登場しない判断は「観察候補」として別枠で提示し、採用を急がない

## 関連Skill

- `[[detect-ambiguity]]` — ログの書き込み元
- `[[review-spec]]` — ログの書き込み元
- `[[generate-sequence]]` — ログの書き込み元
- `[[specflow-pipeline]]` — パイプライン完了後にこのSkillを案内する
