---
name: detect-ambiguity
description: Detect ambiguities in a requirements document and supplement them with formal definitions (sets, predicates, state transitions). Use when the user provides a requirements/specification document (often a .txt or .md file) and asks to analyze ambiguity, find unclear expressions, or convert natural language to formal definitions. Outputs a structured Japanese report plus a fully-revised specification.
---

# detect-ambiguity

要件定義書の曖昧性を検出し、形式的定義で補完するSkill。

## いつ使うか

- ユーザーが `.txt` / `.md` の要件定義書を提示し「曖昧性を検出」「形式的に書き直して」と依頼したとき
- `/specflow-pipeline` の第1ステップとして呼ばれたとき
- 仕様書のレビュー前準備として、明確性の土台を整えたいとき

## 手順

1. 入力となる要件定義書のパスまたは本文をユーザーから受け取る
   - ファイルパスが渡されたら `Read` ツールで読み込む
   - 本文が直接渡されたらそのまま使う
2. [prompts/ambiguity.md](../../../prompts/ambiguity.md) を読み込み、システムプロンプトとして使用する
3. 以下の構造でレポートを生成する：
   - `## 曖昧性検出レポート`
   - `### 検出された曖昧箇所` — 箇所・種別・問題・影響
   - `### 形式的定義による補完` — 集合論・述語論理・状態遷移
   - `### 補完済み要件定義書` — 全文（省略禁止）
4. ユーザーが指定する場合、結果を `docs/ambiguity-report.md` に保存する
5. 補完済み仕様書部分は `docs/specification.md` への保存候補としてユーザーに提示する

## 出力の品質基準

- 検出された曖昧箇所が **最低5箇所** あること（要件が短い場合を除く）
- 形式的定義に少なくとも1つの数学記法（集合、関数、状態遷移）が含まれること
- 補完済み要件定義書は元の要件の全項目をカバーすること

## 関連Skill

- `[[four-pillars-review]]` — 曖昧性除去後に4本柱でレビュー
- `[[generate-sequence]]` — 補完済み仕様からシーケンス図生成
- `[[specflow-pipeline]]` — 全工程をオーケストレーション
