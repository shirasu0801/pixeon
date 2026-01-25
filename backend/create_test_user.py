"""
テストユーザーを作成するスクリプト
"""
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from app.db.database import SessionLocal, init_db
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.exc import IntegrityError

def create_test_user():
    """テストユーザーを作成"""
    # データベースを初期化
    init_db()
    
    db = SessionLocal()
    
    try:
        # テストユーザーの情報
        test_users = [
            {
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass123"
            },
            {
                "username": "admin",
                "email": "admin@example.com",
                "password": "admin1234"
            },
            {
                "username": "demo",
                "email": "demo@example.com",
                "password": "demo1234"
            }
        ]
        
        created_users = []
        skipped_users = []
        
        for user_data in test_users:
            # 既存ユーザーのチェック
            existing_user = db.query(User).filter(
                (User.username == user_data["username"]) | 
                (User.email == user_data["email"])
            ).first()
            
            if existing_user:
                print(f"[SKIP] ユーザー '{user_data['username']}' は既に存在します（スキップ）")
                skipped_users.append(user_data["username"])
                continue
            
            # パスワードをハッシュ化（72バイト制限に対応）
            password = user_data["password"]
            if len(password.encode('utf-8')) > 72:
                password = password[:72]
            hashed_password = get_password_hash(password)
            
            # ユーザーを作成
            new_user = User(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=hashed_password
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            created_users.append({
                "username": user_data["username"],
                "email": user_data["email"]
            })
            
            print(f"[OK] ユーザー '{user_data['username']}' を作成しました")
        
        print("\n" + "="*50)
        print("テストユーザー作成完了")
        print("="*50)
        print("\n作成されたユーザー:")
        for user in created_users:
            print(f"  ユーザー名: {user['username']}")
            print(f"  メール: {user['email']}")
            print()
        
        if skipped_users:
            print("スキップされたユーザー:")
            for username in skipped_users:
                print(f"  - {username}")
            print()
        
        print("ログイン情報:")
        print("-" * 50)
        for user_data in test_users:
            if user_data["username"] not in skipped_users:
                print(f"ユーザー名: {user_data['username']}")
                print(f"パスワード: {user_data['password']}")
                print()
        
    except IntegrityError as e:
        db.rollback()
        print(f"エラー: データベースエラーが発生しました: {e}")
        sys.exit(1)
    except Exception as e:
        db.rollback()
        print(f"エラー: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    print("テストユーザーを作成しています...")
    print()
    create_test_user()
