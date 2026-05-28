---
name: generate-sequence
description: Generate a Mermaid sequence diagram (sequenceDiagram) from a requirements/specification document. Use when the user asks to create, draw, or visualize a sequence diagram from spec content. Output is Japanese-labeled Mermaid code with error paths, alt/opt/loop, and spec-reference comments.
---

# generate-sequence

要件定義書からMermaidシーケンス図を生成するSkill。

## いつ使うか

- ユーザーが「シーケンス図を作って」と要件定義書を渡したとき
- `/specflow-pipeline` の図生成ステップとして呼ばれたとき

## 手順

1. 仕様書（パス or 本文）を取得
2. [prompts/sequence.md](../../../prompts/sequence.md) をシステムプロンプトとして使用
3. 以下を含む図を生成：
   - `sequenceDiagram` ヘッダ
   - 主要参加者（5〜7推奨）
   - 主要ユースケースのフロー
   - エラーパス（最低1本）
   - 並行処理は `par`、条件分岐は `alt`/`opt`、繰り返しは `loop`
   - 末尾コメント `%% 仕様参照: docs/specification.md` と `%% 生成日時: <YYYY-MM-DD HH:MM>`
4. 出力前にコードを ` ```mermaid ` と ` ``` ` で囲む
5. 図の前に「設計上のポイント」を3〜5項目で記述
6. ユーザー指定があれば `docs/sequence.md` に保存（テンプレートは `make_diagram_doc` 互換）

## 自己点検

生成後に以下をチェック：
- すべての主要ユースケースを網羅したか
- エラーパスが含まれているか
- 参加者数が適切か（5〜7）
- メッセージ名が動詞句で明確か

## 関連Skill

- `[[refine-sequence]]` — 生成後のインタラクティブ修正
- `[[generate-class-diagram]]`, `[[generate-er-diagram]]`, `[[generate-flowchart]]` — 他図種
