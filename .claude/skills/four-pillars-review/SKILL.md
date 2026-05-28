---
name: four-pillars-review
description: The canonical 4-pillar specification review methodology used by SpecFlow — Clarity → Completeness → Consistency → Feasibility, evaluated in strict order with documented dependencies between pillars. Use when the user wants to understand HOW reviews are performed, the order/methodology of the four pillars, or wants to apply just one pillar in isolation. This skill documents the order, the "why" behind the order, and the per-pillar checklist.
---

# four-pillars-review

仕様駆動開発における4本柱レビューの**方法論本体**。`review-spec` Skill から内部参照される。

詳細プロンプトは [prompts/four-pillars.md](../../../prompts/four-pillars.md) を参照。

## なぜ4本柱なのか

要件定義書の質は単一の尺度では測れない。4つの独立した観点で測定し、それぞれに固有のチェック手法を当てる必要がある。

## なぜ「この順序」なのか

```
明確性 → 完全性 → 一貫性 → 実装可能性
```

| 順番 | 柱 | 前提 | 順序の理由 |
|------|-----|------|------------|
| 1 | 明確性 | なし | 曖昧な文は読み手で解釈が分かれ、後段の判定自体が成立しない |
| 2 | 完全性 | 明確性 | 曖昧な要件では「何が抜けているか」を判定できない |
| 3 | 一貫性 | 明確性＋完全性 | 明確かつ揃った要件であってこそ、内部矛盾を比較判定できる |
| 4 | 実装可能性 | 1〜3すべて | 明確・完全・一貫した要件を前提に、現実の制約で検証する最終ゲート |

**順序の入れ替えは禁止**。例えば実装可能性を先に判定すると、曖昧な要件を「実装不可能」と誤判定するか、「曖昧なまま実装」を許容してしまう。

## 各柱の具体手順

### 柱1: 明確性 (Clarity)

1. 主語の省略をスキャン
2. 指示語（それ・この・当該）の多義性をスキャン
3. 数量・順序・方向の曖昧表現をスキャン
4. 未定義の用語をスキャン
5. 自然言語のまま残る形式化可能箇所をスキャン

→ 出力: 曖昧箇所リスト＋形式的補完案

### 柱2: 完全性 (Completeness)

1. Why（課題・背景・KPI）の有無
2. What（機能・入出力・データ型）の有無
3. 境界条件（上限・下限・空・null・並行）の網羅
4. エラー処理・異常系の定義
5. 非機能要件（性能・可用性・セキュリティ）
6. 前提条件（環境・依存・運用前提）

→ 出力: 不足項目リスト＋補完記述案

### 柱3: 一貫性 (Consistency)

1. 用語の一貫性（同一概念の異名）
2. 値の一貫性（閾値・上限の食い違い）
3. 論理の一貫性（同時非両立な要件）
4. 粒度の一貫性（抽象度の段差）
5. 参照の一貫性（図表参照の正誤）

→ 出力: 矛盾箇所の対照表

### 柱4: 実装可能性 (Feasibility)

1. 技術的実現性
2. 性能的実現性
3. コスト実現性
4. スケジュール実現性
5. 運用実現性
6. テスト実現性

→ 出力: 実現困難要件＋代替案

## 単一柱モード

ユーザーが「明確性だけチェックして」のように単一柱を指定した場合、その柱だけを実行する。
ただし、その柱が前提とする上位柱が満たされない可能性を警告する。

## 関連Skill

- `[[review-spec]]` — 4本柱を統合実行
- `[[detect-ambiguity]]` — 柱1を独立した深掘りSkillとして実行
