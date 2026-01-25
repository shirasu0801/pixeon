# バックエンド API

FastAPIを使用した画像認識APIサーバーです。

## セットアップ

1. 仮想環境を作成（推奨）
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 依存関係をインストール
```bash
pip install -r requirements.txt
```

3. 環境変数を設定
```bash
cp .env.example .env
# .envファイルを編集してSECRET_KEYなどを設定
```

4. データベースを初期化
```bash
python -c "from app.db.database import init_db; init_db()"
```

## 実行

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

APIドキュメントは以下のURLで確認できます:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 環境変数

- `SECRET_KEY`: JWTトークンの署名に使用する秘密鍵
- `DATABASE_URL`: データベース接続URL
- `LOCAL_STORAGE_PATH`: ローカル開発時の画像保存先
- `MAX_FILE_SIZE_MB`: 最大ファイルサイズ（MB）

## APIエンドポイント

### 認証
- `POST /api/auth/register` - ユーザー登録
- `POST /api/auth/login` - ログイン
- `GET /api/auth/me` - 現在のユーザー情報取得

### 画像解析
- `POST /api/detect` - 画像アップロードと解析
- `GET /api/history` - 解析履歴取得
- `GET /api/history/{id}` - 履歴詳細取得
- `DELETE /api/history/{id}` - 履歴削除
