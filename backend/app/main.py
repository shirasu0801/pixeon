from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth, detection
from app.db.database import init_db
from app.core.config import settings
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime, timedelta
import os

# ログ設定
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 10日間保持するログファイルハンドラー
log_file = log_dir / "app.log"
handler = RotatingFileHandler(
    log_file,
    maxBytes=10 * 1024 * 1024,  # 10MB
    backupCount=10
)
handler.setLevel(logging.ERROR)  # error以上のログのみ
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

# ロガー設定
logger = logging.getLogger()
logger.setLevel(logging.ERROR)
logger.addHandler(handler)

# コンソール出力も追加（開発用）
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

app = FastAPI(
    title="画像認識API",
    description="AIを用いた画像内物体検出API",
    version="1.0.0"
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React開発サーバー
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルーターを登録
app.include_router(auth.router)
app.include_router(detection.router)


@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時の初期化"""
    try:
        init_db()
        
        # ローカルストレージディレクトリを作成
        storage_path = Path(settings.LOCAL_STORAGE_PATH)
        storage_path.mkdir(parents=True, exist_ok=True)
        
        # 静的ファイル配信（ローカル開発用）
        if not settings.AWS_S3_BUCKET:
            uploads_dir = Path(settings.LOCAL_STORAGE_PATH).absolute()
            if uploads_dir.exists():
                try:
                    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
                except Exception as e:
                    logger.warning(f"静的ファイルのマウントに失敗しました: {e}")
        
        logger.info("アプリケーションを起動しました")
    except Exception as e:
        logger.error(f"起動時の初期化に失敗しました: {e}", exc_info=True)


@app.get("/")
def root():
    """ルートエンドポイント"""
    return {"message": "画像認識APIへようこそ"}


@app.get("/health")
def health_check():
    """ヘルスチェック"""
    return {"status": "healthy"}
