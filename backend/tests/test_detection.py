import pytest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_db, Base, engine
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.orm import sessionmaker

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """テスト用データベースセッション"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """テストクライアント"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """テスト用ユーザーを作成"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpass123")
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_token(client, test_user):
    """認証トークンを取得"""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    return response.json()["access_token"]


def test_detect_image_without_auth(client):
    """認証なしでの画像解析テスト"""
    # ダミー画像を作成
    image_data = io.BytesIO()
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='red')
    img.save(image_data, format='PNG')
    image_data.seek(0)
    
    response = client.post(
        "/api/detect",
        files={"file": ("test.png", image_data, "image/png")}
    )
    assert response.status_code == 401


def test_detect_invalid_file_type(client, auth_token):
    """無効なファイル形式のテスト"""
    response = client.post(
        "/api/detect",
        files={"file": ("test.txt", b"not an image", "text/plain")},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 400


def test_get_history_without_auth(client):
    """認証なしでの履歴取得テスト"""
    response = client.get("/api/history")
    assert response.status_code == 401


def test_get_history_with_auth(client, auth_token):
    """認証ありでの履歴取得テスト"""
    response = client.get(
        "/api/history",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
