# シーケンス図

> 最終更新: 2026-05-29
> 生成ツール: SpecFlow（仕様駆動開発アシスタント）

---

## 設計上のポイント

1. **非同期メール送信はキュー経由** — §1.6「トランザクション完了後に非同期で実行」に従い、`DBコミット → メールキューへエンキュー` の順序を図示。
2. **inactive重複フローの2分岐** — §1.4の再アクティブ化「同意/拒否」が異なる後続処理を持つため、ネストaltで表現。
3. **partial unique indexの可視化** — §1.6のDB制約をアプリ層の重複チェック + DBコミット時の安全網として図に表現。
4. **検索結果の在庫状況別出し分け** — §2.3の3状態（CHECKED_OUT / RESERVED_PICKUP_WAITING / AVAILABLE）ごとに返却日フィールドをaltで出し分け。
5. **loopの早期終了をaltで補完** — Mermaidのloop構文は早期脱出を表現できないため、alt（成功時ループ終了）で補足。

---

```mermaid
sequenceDiagram
    participant U as 利用者
    participant API as APIサーバー
    participant DB as DBサーバー
    participant MQ as メールキュー
    participant MS as メールサービス

    note over U,MS: ── §1 利用者登録フロー ──

    U->>API: POST /users（氏名・メール・電話番号）

    alt バリデーションエラー（§1.3）
        API-->>U: 400 Bad Request（エラーメッセージ）
    else 入力値OK
        API->>DB: activeユーザー内でメール重複チェック（§1.4）
        DB-->>API: チェック結果

        alt 重複あり／active（§1.4）
            API-->>U: 409 Conflict（利用者ID提示・ログイン誘導）
        else 重複あり／inactive（§1.4）
            API-->>U: 再アクティブ化の選択肢を提示
            alt 再アクティブ化に同意
                U->>API: 同意
                API->>DB: BEGIN TX：activeに更新 ＋ 通知ログ挿入
                DB-->>API: COMMIT
                API->>MQ: メール送信タスクをエンキュー（§1.6）
                API-->>U: 200 OK（既存利用者ID）
            else 拒否 → 新規登録（§1.4）
                U->>API: 拒否
                API->>DB: BEGIN TX：新規レコード挿入（AUTOINCREMENT）＋ 通知ログ挿入
                note right of DB: 電話番号はハイフン除去後保存（§1.5）
                DB-->>API: COMMIT（新規利用者ID）
                API->>MQ: メール送信タスクをエンキュー（§1.6）
                API-->>U: 201 Created（新規利用者ID）
            end
        else 重複なし／新規登録（§1.5）
            API->>DB: BEGIN TX：新規レコード挿入（AUTOINCREMENT）＋ 通知ログ挿入
            note right of DB: 電話番号はハイフン除去後保存（§1.5）
            DB-->>API: COMMIT（利用者ID）
            API->>MQ: メール送信タスクをエンキュー（§1.6）
            API-->>U: 201 Created（利用者ID）
        end
    end

    note over MQ,MS: ── §1.5 登録完了メール送信（非同期） ──

    loop リトライ最大3回（1分→2分→4分）（§1.5）
        MQ->>MS: メール送信リクエスト
        alt 送信成功（ループ終了）
            MS-->>MQ: 送信完了
        else 送信失敗
            MS-->>MQ: エラー返却（次回リトライへ）
        end
    end

    opt 3回連続失敗後（§1.5）
        MQ->>API: 管理者アラート通知
    end

    note over U,DB: ── §2 蔵書検索フロー ──

    U->>API: GET /books?title=〇〇&author=〇〇&isbn=〇〇

    alt 検索条件なし（§2.2）
        API-->>U: 400 Bad Request（条件未指定エラー）
    else 検索条件あり
        note right of API: ISBNはハイフン除去後に完全一致比較（§0.1）
        API->>DB: SELECT books（AND条件・部分一致/完全一致）（§2.2）
        DB-->>API: 書籍リスト

        alt CHECKED_OUT の書籍を含む（§2.3）
            note right of API: 返却予定日をJSTで付加
        else RESERVED_PICKUP_WAITING の書籍を含む（§2.3）
            note right of API: 予約取置き期限をJSTで付加
        else AVAILABLE のみ（§2.3）
            note right of API: 日付フィールドは含めない
        end

        API-->>U: 200 OK（書籍リスト・在庫状況・日付 JST表示）
    end

    %% 仕様参照: docs/specification.md
    %% 生成日時: 2026-05-29 10:00
```
