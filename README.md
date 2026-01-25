# 画像認識アプリケーション

AI（YOLOv8）を用いた画像内物体検出アプリケーションです。ユーザーが画像をアップロードすると、AIが自動的に物体を検出し、その名称と位置を表示します。

## 機能

- **ユーザー認証**: JWT認証によるユーザー登録・ログイン
- **画像アップロード**: JPG/PNG形式の画像をアップロード
- **物体検出**: YOLOv8モデルによる高精度な物体検出
- **結果表示**: 検出された物体をバウンディングボックスとラベルで表示
- **履歴管理**: 過去の解析結果を保存・閲覧・削除

## 技術スタック

### バックエンド
- **フレームワーク**: FastAPI
- **言語**: Python 3.9+
- **MLモデル**: YOLOv8 (ultralytics)
- **データベース**: SQLite（開発環境）
- **認証**: JWT

### フロントエンド
- **フレームワーク**: React 19
- **言語**: TypeScript
- **ビルドツール**: Vite
- **UIライブラリ**: Material-UI

## セットアップ

### 前提条件

- Python 3.9以上
- Node.js 18以上
- npm または yarn

### Windowsの場合

1. `start_servers.bat` をダブルクリックして実行
2. ブラウザで http://localhost:5173 にアクセス

### 手動で起動する場合

### バックエンドのセットアップ

1. バックエンドディレクトリに移動
```bash
cd backend
```

2. 仮想環境を作成（推奨）
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. 依存関係をインストール
```bash
pip install -r requirements.txt
```

4. 環境変数を設定
```bash
# .envファイルを作成（.env.exampleを参考に）
# SECRET_KEYを変更してください
```

# .envファイルを作成（初回のみ）
# .envファイルに以下を記述:
# SECRET_KEY=dev-secret-key-change-in-production-12345
# ALGORITHM=HS256
# ACCESS_TOKEN_EXPIRE_MINUTES=30
# DATABASE_URL=sqlite:///./pixeon.db
# LOCAL_STORAGE_PATH=./uploads
# MAX_FILE_SIZE_MB=10

5. データベースを初期化
```bash
python -c "from app.db.database import init_db; init_db()"
```

6. テストユーザーを作成（オプション）
```bash
python create_test_user.py
```

7. サーバーを起動
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

バックエンドAPIは http://localhost:8000 で起動します。
APIドキュメント: http://localhost:8000/docs

### フロントエンドのセットアップ

1. フロントエンドディレクトリに移動
```bash
cd frontend
```

2. 依存関係をインストール
```bash
npm install
```

3. 開発サーバーを起動
```bash
npm run dev
```

フロントエンドは http://localhost:5173 で起動します。

### ポートが既に使用されている場合

- バックエンド: `--port` オプションで別のポートを指定
- フロントエンド: `vite.config.js` でポートを変更

### データベースエラー

```bash
cd backend
python -c "from app.db.database import init_db; init_db()"
```

### 依存関係のエラー

```bash
# バックエンド
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# フロントエンド
cd frontend
npm install
```

## 使用方法

1. アプリケーションにアクセス（http://localhost:5173）
2. 新規登録またはログイン
3. 「画像を選択」ボタンから画像をアップロード
4. 「物体を検出」ボタンをクリック
5. 検出結果が画像上に表示されます
6. 「履歴」ページで過去の解析結果を確認できます

## テストユーザー

以下のテストユーザーがデータベースに登録されています：

| ユーザー名 | メールアドレス | パスワード |
|-----------|--------------|-----------|
| testuser | test@example.com | testpass123 |
| admin | admin@example.com | admin1234 |
| demo | demo@example.com | demo1234 |

### テストユーザーの作成

```bash
cd backend
python create_test_user.py
```

詳細は `backend/TEST_USERS.md` を参照してください。

## テスト

### バックエンドのテスト

```bash
cd backend
pytest tests/
```

## プロジェクト構造

```
pixeon/
├── backend/                 # バックエンド（FastAPI）
│   ├── app/
│   │   ├── api/            # APIエンドポイント
│   │   ├── core/           # 設定、セキュリティ、ストレージ
│   │   ├── db/             # データベース設定
│   │   ├── ml/             # MLモデル（YOLOv8）
│   │   ├── models/         # データベースモデル
│   │   ├── schemas/        # Pydanticスキーマ
│   │   └── main.py         # アプリケーションエントリーポイント
│   ├── tests/              # テストコード
│   ├── uploads/            # アップロードされた画像（ローカル開発用）
│   ├── .env.example        # 環境変数のテンプレート
│   ├── create_test_user.py # テストユーザー作成スクリプト
│   └── requirements.txt    # Python依存関係
├── frontend/               # フロントエンド（React）
│   ├── src/
│   │   ├── api/            # APIクライアント
│   │   ├── components/     # Reactコンポーネント
│   │   ├── contexts/       # React Context
│   │   ├── pages/         # ページコンポーネント
│   │   └── App.tsx        # メインアプリケーション
│   └── package.json       # Node.js依存関係
├── .gitignore             # Git除外設定
├── requirements.md        # 要件定義書
└── README.md             # このファイル
```

## 環境変数

### バックエンド (.env)

`.env.example` をコピーして `.env` を作成し、以下の値を設定してください：

```env
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./pixeon.db
LOCAL_STORAGE_PATH=./uploads
MAX_FILE_SIZE_MB=10

# AWS設定（本番環境用）
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=ap-northeast-1
AWS_S3_BUCKET=
```

### フロントエンド (.env)

```env
VITE_API_BASE_URL=http://localhost:8000
```

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

詳細は http://localhost:8000/docs で確認できます。

## セキュリティ

### GitHubにプッシュする前に

以下のファイルは機密情報を含むため、`.gitignore`で除外されています：

- `.env` - 環境変数（SECRET_KEYなど）
- `*.db` - データベースファイル
- `uploads/` - アップロードされた画像
- `logs/` - ログファイル

**重要**: `.env`ファイルは絶対にGitにコミットしないでください。代わりに`.env.example`を使用してください。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 注意事項

- 初回実行時、YOLOv8モデル（yolov8n.pt）が自動的にダウンロードされます
- ローカル開発環境では画像は`backend/uploads`ディレクトリに保存されます
- 本番環境ではAWS S3への保存を推奨します
- パスワードは8文字以上である必要があります
