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
2. **[透明性] 使用Skill出力**：このSKILL.mdの全文をコードブロックで出力する（後述「透明性出力」参照）
3. [prompts/sequence.md](../../../prompts/sequence.md) をシステムプロンプトとして使用
4. 以下を含む図を生成：
   - `sequenceDiagram` ヘッダ
   - 主要参加者（5〜7推奨）
   - 主要ユースケースのフロー
   - エラーパス（最低1本）
   - 並行処理は `par`、条件分岐は `alt`/`opt`、繰り返しは `loop`
   - 末尾コメント `%% 仕様参照: docs/specification.md` と `%% 生成日時: <YYYY-MM-DD HH:MM>`
5. 出力前にコードを ` ```mermaid ` と ` ``` ` で囲む
6. 図の前に「設計上のポイント」を3〜5項目で記述
7. ユーザー指定があれば `docs/sequence.md` に保存（テンプレートは `make_diagram_doc` 互換）
8. **[透明性] 推論ログ・暗黙知追記を出力する**（後述「透明性出力」参照）

## 自己点検

生成後に以下をチェック：
- すべての主要ユースケースを網羅したか
- エラーパスが含まれているか
- 参加者数が適切か（5〜7）
- メッセージ名が動詞句で明確か

## 透明性出力（毎回必須）

このSkillを実行するたびに、以下の3ブロックを出力することで、人間がAIの判断を検証・修正できるようにする。

### ブロック1: 使用Skill（実行冒頭）

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
【使用Skill: generate-sequence】
（このSKILL.mdの全文をここに貼り付け）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### ブロック2: 設計判断ログ（図の直後）

各設計判断について以下の形式で記録する。
判断の根拠が「仕様内」か「暗黙知（仕様外推論）」かを明示することが最重要。

```
## 設計判断ログ

| # | 判断内容 | 根拠種別 | 根拠の詳細 |
|---|---------|---------|-----------|
| 1 | 参加者にXXXを追加した | 仕様内 | 仕様書§2.3「XXX」の記述による |
| 2 | エラーパスにYYYを追加した | 暗黙知 | 仕様に明記なし。一般的なWebシステムでは認証失敗は必須エラーパスと判断 |
| 3 | loop構文でZZZを表現した | 仕様内+暗黙知 | §3.1に「繰り返し」の記述あり。回数は未定義のためloopで抽象化 |
```

### ブロック3: 暗黙知追記サマリ（出力末尾）

仕様書に**明記されていないが**追加した要素を一覧化する。
人間がここを見て「不要」と判断したらSKILL.mdを修正する。

```
## 暗黙知追記サマリ

以下は仕様書に明示されていないが、AIが暗黙知・一般慣習・設計原則に基づき追加した内容です。
誤りや不要な追記があれば、SKILL.mdの「手順」または「自己点検」セクションを修正してください。

| 追記内容 | 使用した暗黙知・前提 | 修正が必要な場合 |
|---------|-------------------|---------------|
| 〇〇を参加者に追加 | REST APIにはAPIゲートウェイが存在するという一般知識 | 不要であればSKILL.md手順3から除外 |
| エラー時の通知フロー | システム障害時は管理者通知が標準的 | 不要であれば自己点検チェックリストに「通知フロー不要」を追記 |
```

## 関連Skill

- `[[refine-sequence]]` — 生成後のインタラクティブ修正
- `[[generate-class-diagram]]`, `[[generate-er-diagram]]`, `[[generate-flowchart]]` — 他図種
