from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # JWT設定
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # データベース
    DATABASE_URL: str = "sqlite:///./pixeon.db"

    # AWS設定
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-northeast-1"
    AWS_S3_BUCKET: Optional[str] = None

    # ローカル開発設定
    LOCAL_STORAGE_PATH: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
