---
name: generate-er-diagram
description: Generate a Mermaid erDiagram (entity-relationship) from a specification, focusing on data model and cardinality. Use when the user wants to design or visualize a relational/document database schema.
---

# generate-er-diagram

要件からMermaid ER図を生成するSkill。

## 手順

1. 仕様書から永続化が必要なエンティティを抽出
2. 各エンティティのPK/FK/属性を推論
3. 関係を `||--o{` などのMermaid記法で表現
4. Mermaid `erDiagram` を生成：
   ```mermaid
   erDiagram
     USER ||--o{ LOAN : "borrows"
     BOOK ||--o{ LOAN : "lent_in"
     USER {
       int id PK
       string name
       string email
     }
   ```

## カーディナリティ表

| 表記 | 意味 |
|------|------|
| `||--||` | 1対1 |
| `||--o{` | 1対多 |
| `}o--o{` | 多対多 |
| `||--o|` | 1対0..1 |

## 関連Skill

- `[[generate-class-diagram]]` — ドメインモデル視点
- `[[generate-sequence]]`, `[[generate-flowchart]]`
