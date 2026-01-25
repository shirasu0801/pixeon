# テストユーザー情報

## デフォルトテストユーザー

以下のテストユーザーがデータベースに登録されています：

### ユーザー1: testuser
- **ユーザー名**: `testuser`
- **メールアドレス**: `test@example.com`
- **パスワード**: `testpass123`

### ユーザー2: admin
- **ユーザー名**: `admin`
- **メールアドレス**: `admin@example.com`
- **パスワード**: `admin1234`

### ユーザー3: demo
- **ユーザー名**: `demo`
- **メールアドレス**: `demo@example.com`
- **パスワード**: `demo1234`

## テストユーザーの作成方法

### 方法1: スクリプトを実行（推奨）

```bash
cd backend
python create_test_user.py
```

### 方法2: Pythonから直接実行

```bash
cd backend
python -c "from create_test_user import create_test_user; create_test_user()"
```

## 注意事項

- テストユーザーは既に存在する場合はスキップされます
- 本番環境ではこれらのテストユーザーを削除してください
- パスワードは開発環境用の簡単なものです

## ログイン方法

1. ブラウザで http://localhost:5173 にアクセス
2. ログイン画面で上記のユーザー名とパスワードを入力
3. 「ログイン」ボタンをクリック

## テストユーザーの削除

データベースから直接削除する場合：

```python
from app.db.database import SessionLocal
from app.models.user import User

db = SessionLocal()
test_user = db.query(User).filter(User.username == "testuser").first()
if test_user:
    db.delete(test_user)
    db.commit()
db.close()
```
