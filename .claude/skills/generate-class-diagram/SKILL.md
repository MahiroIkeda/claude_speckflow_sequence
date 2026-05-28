---
name: generate-class-diagram
description: Generate a Mermaid classDiagram from a specification or domain description. Use when the user wants a class/object structure diagram, type hierarchy, or DDD-style domain model visualization (not for sequence/flow/ER).
---

# generate-class-diagram

要件・ドメイン記述からMermaidクラス図を生成するSkill。

## 手順

1. 仕様書または「クラス図を作りたい対象」をユーザーから受け取る
2. ドメインのエンティティを抽出（名詞・概念）
3. 各エンティティの属性・メソッドを推論
4. 関係（継承・関連・集約・コンポジション）を抽出
5. Mermaid `classDiagram` を生成：
   ```mermaid
   classDiagram
     class Book {
       +String title
       +String isbn
       +borrow(user)
     }
     class User
     Book --> User : borrowedBy
   ```
6. コード末尾に `%% 仕様参照: docs/specification.md` と `%% 生成日時: ...` を追加

## 設計品質

- エンティティ数は10以下を推奨（多すぎる場合は分割提案）
- 関係はラベル付きで方向を明示
- 抽象クラス/インターフェースは `<<abstract>>` / `<<interface>>` で示す

## 関連Skill

- `[[generate-sequence]]`, `[[generate-er-diagram]]`, `[[generate-flowchart]]`
