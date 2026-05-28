---
name: generate-flowchart
description: Generate a Mermaid flowchart (TD/LR) from a business process or algorithm description. Use when the user wants to visualize a decision flow, state machine, or workflow that is NOT primarily about message-passing between actors (use generate-sequence for that).
---

# generate-flowchart

業務プロセス・アルゴリズムからMermaidフローチャートを生成するSkill。

## 手順

1. プロセス記述から開始ノード・終了ノード・判定ノード・処理ノードを抽出
2. レイアウトを選択：`TD`（上→下）か `LR`（左→右）
3. Mermaid `flowchart` を生成：
   ```mermaid
   flowchart TD
     Start([開始]) --> Check{在庫あり?}
     Check -->|Yes| Lend[貸出処理]
     Check -->|No| Reserve[予約処理]
     Lend --> End([終了])
     Reserve --> End
   ```

## ノード形状の使い分け

- `([])` — 開始/終了
- `[]` — 処理
- `{}` — 判定
- `[/...\\]` — 入力
- `[\\.../]` — 出力

## 関連Skill

- `[[generate-sequence]]` — メッセージ通信視点
- `[[generate-class-diagram]]`, `[[generate-er-diagram]]`
