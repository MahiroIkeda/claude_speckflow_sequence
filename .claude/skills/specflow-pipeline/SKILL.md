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

## 透明性出力（毎回必須）

パイプライン実行中に以下の透明性情報を出力する。

### パイプライン開始時（ステップ0）

```
## パイプライン実行計画

| ステップ | Skill | 目的 | 予想される主要判断 |
|--------|-------|------|-----------------|
| 1 | detect-ambiguity | 曖昧性除去 | 自然言語による補完 |
| 2 | review-spec | 4本柱レビュー | 優先度付き改善提案 |
| 3 | generate-sequence | シーケンス図生成 | 参加者・フローの設計判断 |
| 4 | detect-spec-diff | 差分検出 | 変更の影響範囲判定 |
| 5 | save/PR | GitHub反映 | ユーザー選択 |
```

### 各ステップ完了時の引き継ぎログ

各ステップ完了後、次ステップに渡す判断内容を記録する。

```
## ステップN 完了 → ステップN+1 への引き継ぎ

**完了したこと**: [ステップNで生成・決定した内容]
**次ステップへの入力**: [次のSkillに渡す主な情報]
**注意事項（暗黙知を使用した箇所）**: [次ステップで人間確認を推奨する判断]
**スキップ/停止の判断**: [ステップを省略・中断した場合はその理由]
```

### パイプライン完了時の総合暗黙知サマリ

```
## パイプライン全体 暗黙知追記サマリ

全ステップを通じて、仕様書に明記されていないが追加・補完した内容の総一覧。

| ステップ | 追記内容 | 使用した暗黙知 | 関連SKILL.md |
|--------|---------|--------------|-------------|
| 1 | 〇〇を補完 | 〇〇という一般知識 | detect-ambiguity/SKILL.md |
| 2 | 非機能要件を追記 | 〇〇という設計原則 | review-spec/SKILL.md |
| 3 | エラーパスを追加 | 〇〇という慣習 | generate-sequence/SKILL.md |

**Skillの修正が推奨される箇所**: [人間がレビューすべきSKILL.mdと修正内容の提案]
```

## 出力ファイル配置

- `docs/specification.md` — 最終仕様
- `docs/sequence.md` — 最終シーケンス図
- `docs/ai-decision-log.md` — AI意思決定ログ（各ステップが自動追記）
- `docs/ambiguity-report.md` — 曖昧性レポート（任意）
- `docs/review-report.md` — レビューレポート（任意）

## パイプライン完了後の推奨アクション

パイプライン完了後、ユーザーに以下を案内する：

```
## 次のステップ

docs/ai-decision-log.md にAIの判断根拠が蓄積されました。

【推奨】ログを確認してSkillを改善する場合：
  /refine-skills-from-log
  → ログのパターンを分析し、SKILL.md改善案を生成します
  → 採用した改善案はskill-creatorでさらに構造最適化できます
```

## 関連Skill

すべてのSpecFlow関連Skillを参照する：
- `[[detect-ambiguity]]`, `[[review-spec]]`, `[[four-pillars-review]]`
- `[[generate-sequence]]`, `[[refine-sequence]]`
- `[[detect-spec-diff]]`, `[[save-spec-git]]`, `[[create-spec-pr]]`
- `[[refine-skills-from-log]]` — ログからSKILL.md改善案を生成
