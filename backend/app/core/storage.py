import os
import uuid
from pathlib import Path
from typing import Optional
import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

_s3_client = None


def get_s3_client():
    """S3クライアントを取得"""
    global _s3_client
    if _s3_client is None and settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        _s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
    return _s3_client


def save_image(file_content: bytes, filename: str) -> str:
    """
    画像を保存（ローカルまたはS3）
    
    Args:
        file_content: ファイルのバイトデータ
        filename: 元のファイル名
        
    Returns:
        保存された画像のパスまたはURL
    """
    # ファイル拡張子を取得
    ext = Path(filename).suffix
    # 一意のファイル名を生成
    unique_filename = f"{uuid.uuid4()}{ext}"
    
    # S3が設定されている場合はS3に保存
    s3_client = get_s3_client()
    if s3_client and settings.AWS_S3_BUCKET:
        try:
            s3_key = f"images/{unique_filename}"
            s3_client.put_object(
                Bucket=settings.AWS_S3_BUCKET,
                Key=s3_key,
                Body=file_content,
                ContentType=f"image/{ext[1:].lower()}"
            )
            # S3のURLを返す
            url = f"https://{settings.AWS_S3_BUCKET}.s3.{settings.AWS_REGION}.amazonaws.com/{s3_key}"
            logger.info(f"画像をS3に保存しました: {url}")
            return url
        except ClientError as e:
            logger.error(f"S3への保存に失敗しました: {e}")
            raise
    
    # ローカルに保存
    storage_path = Path(settings.LOCAL_STORAGE_PATH)
    storage_path.mkdir(parents=True, exist_ok=True)
    
    file_path = storage_path / unique_filename
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    logger.info(f"画像をローカルに保存しました: {file_path}")
    return str(file_path)


def get_image_path(stored_path: str) -> str:
    """
    保存された画像のパスを取得（ローカル開発用）
    
    Args:
        stored_path: 保存時のパスまたはURL
        
    Returns:
        実際のファイルパス
    """
    # S3のURLの場合はそのまま返す
    if stored_path.startswith("http"):
        return stored_path
    
    # ローカルパスの場合
    return stored_path


def delete_image(image_path: str) -> bool:
    """
    画像を削除
    
    Args:
        image_path: 画像のパスまたはURL
        
    Returns:
        削除成功かどうか
    """
    # S3のURLの場合
    if image_path.startswith("http") and settings.AWS_S3_BUCKET:
        s3_client = get_s3_client()
        if s3_client:
            try:
                # URLからキーを抽出
                key = image_path.split(f"{settings.AWS_S3_BUCKET}.s3")[-1].lstrip("/")
                s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET, Key=key)
                logger.info(f"S3から画像を削除しました: {image_path}")
                return True
            except ClientError as e:
                logger.error(f"S3からの削除に失敗しました: {e}")
                return False
    
    # ローカルファイルの場合
    try:
        if os.path.exists(image_path):
            os.remove(image_path)
            logger.info(f"ローカルから画像を削除しました: {image_path}")
            return True
    except Exception as e:
        logger.error(f"ローカルからの削除に失敗しました: {e}")
        return False
    
    return False
