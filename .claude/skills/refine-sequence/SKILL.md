---
name: refine-sequence
description: Refine an existing Mermaid sequence diagram based on a natural-language change request (e.g., "add an error handler", "swap A and B's order"). Use when the user has an existing sequence diagram and wants targeted edits without regenerating from scratch.
---

# refine-sequence

既存のMermaidシーケンス図に対する修正要求を反映するSkill。

## いつ使うか

- ユーザーが既存のMermaidコードを提示して修正を依頼したとき
- `docs/sequence.md` を更新する必要があるとき

## 手順

1. 現在のMermaidコードと修正依頼文をユーザーから受け取る
   - コードはコードブロックで渡される場合、ファイルパス指定の場合がある
2. [prompts/refine.md](../../../prompts/refine.md) をシステムプロンプトとして使用
3. 修正要求が曖昧な場合は、解釈を1〜2文で明示してから図を提示する
4. 既存構造を尊重し、不要な書き換えを避ける
5. 末尾コメント `%% 仕様参照: ...` と `%% 生成日時: ...` を維持または更新
6. 出力は ` ```mermaid ` と ` ``` ` で囲む

## 関連Skill

- `[[generate-sequence]]` — ゼロから図を生成
- `[[save-spec-git]]` — 修正後の図をGitHubに保存
