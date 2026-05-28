# シーケンス図

> 最終更新: 2026-05-29
> 生成ツール: SpecFlow（仕様駆動開発アシスタント）

---

## 設計上のポイント

1. **認証チェックをaltで切り出し** — §2.1の暫定認証要件（§7定義前）に基づき401チェックを最初の独立altに配置。認証済み以降のバリデーションと分離することでネスト深さを2段以内に制御。
2. **GET /booksエンドポイントをURIとして明記** — v1.4の完全性改善（CP2-001）に基づきエンドポイントパスをリクエスト行に含める。
3. **page < 1境界値エラーをalt分岐に追加** — v1.4補完の「page が1未満は400」を独立elseブランチで表現。
4. **inactiveフローのエンドポイントを更新** — v1.4補完の `POST /users/{existing_user_id}/reactivate` と `POST /users（force_new: true）`、409レスポンスの `action: reactivate_or_new` を反映。
5. **return_due_date/reservation_pickup_deadlineのnull返却を注釈で明示** — §2.3「該当しない状態ではnullを返す」を各書籍状態のnote内で明示。

---

```mermaid
sequenceDiagram
    participant U as 利用者
    participant API as APIサーバー
    participant DB as DBサーバー
    participant MQ as メールキュー
    participant MS as メールサービス

    note over U,MS: §1 利用者登録フロー

    U->>API: POST /users（氏名・メール・電話番号）

    alt バリデーションエラー（§1.3）
        API-->>U: 400 Bad Request（errors配列）
    else 入力値OK
        API->>DB: activeユーザー内でメール重複チェック（§1.4）
        DB-->>API: チェック結果

        alt 重複あり・active（§1.4）
            API-->>U: 409 Conflict（利用者ID提示・ログイン誘導）
        else 重複あり・inactive（§1.4）
            API-->>U: 409 Conflict（action: reactivate_or_new・existing_user_id）
        else 重複なし・新規登録（§1.5）
            API->>DB: BEGIN TX: 新規レコード挿入（AUTOINCREMENT）+ 通知ログ挿入
            note right of DB: 電話番号はハイフン除去後保存（§1.5）
            DB-->>API: COMMIT（利用者ID）
            API->>MQ: メール送信タスクをエンキュー（§1.6）
            API-->>U: 201 Created（利用者ID）
        end
    end

    %% inactiveの場合のみ：再アクティブ化の選択（§1.4）
    alt 再アクティブ化に同意
        U->>API: POST /users/{existing_user_id}/reactivate
        API->>DB: BEGIN TX: activeに更新 + 通知ログ挿入
        DB-->>API: COMMIT
        API->>MQ: メール送信タスクをエンキュー（§1.6）
        API-->>U: 200 OK（既存利用者ID）
    else 拒否・新規登録（§1.4）
        U->>API: POST /users（force_new: true）
        API->>DB: BEGIN TX: 新規レコード挿入（AUTOINCREMENT）+ 通知ログ挿入
        note right of DB: 電話番号はハイフン除去後保存（§1.5）
        DB-->>API: COMMIT（新規利用者ID）
        API->>MQ: メール送信タスクをエンキュー（§1.6）
        API-->>U: 201 Created（新規利用者ID）
    end

    note over MQ,MS: §1.5 登録完了メール送信（非同期）

    loop リトライ最大3回（60秒・120秒・240秒待機）（§1.5）
        MQ->>MS: メール送信リクエスト
        alt 送信成功（ループ終了）
            MS-->>MQ: 送信完了
        else 送信失敗
            MS-->>MQ: エラー返却（次回リトライへ）
        end
    end

    opt 3回連続失敗後（§1.5）
        MQ->>API: 管理者アラートメール送信（設定ファイル定義の管理者宛）
    end

    note over U,DB: §2 蔵書検索フロー

    U->>API: GET /books?title=...&author=...&isbn=...&page=N（§2.1）

    alt 未認証リクエスト（§2.1・§7暫定）
        API-->>U: 401 Unauthorized
    else 認証済み（§7）
        note over API: 入力バリデーション実行
    end

    %% 以下は認証済みの場合のみ（§2.2）
    alt 検索条件なし（§2.2）
        API-->>U: 400 Bad Request（errors配列）
    else page < 1（§2.2）
        API-->>U: 400 Bad Request（errors配列）
    else 検索条件あり・page有効
        note right of API: ISBNはハイフン除去後に完全一致比較（§0.1）
        API->>DB: SELECT books（AND条件・部分一致/完全一致・LIMIT/OFFSET）（§2.2）
        DB-->>API: 書籍リスト（total・page含む）

        alt CHECKED_OUTの書籍を含む（§2.3）
            note right of API: return_due_dateをJSTで付加・reservation_pickup_deadlineはnull
        else RESERVED_PICKUP_WAITINGの書籍を含む（§2.3）
            note right of API: reservation_pickup_deadlineをJSTで付加・return_due_dateはnull
        else AVAILABLEのみ（§2.3）
            note right of API: 両日付フィールドはnull
        end

        API-->>U: 200 OK（書籍リスト・在庫状況・日付 JST表示・ページネーション情報）
        note over API,U: page > 総ページ数の場合はbooks空配列・totalは正しい値（§2.2）
    end

    %% 仕様参照: docs/specification.md
    %% 生成日時: 2026-05-29 12:00
```
