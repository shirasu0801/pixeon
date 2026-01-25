import json
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from PIL import Image
from app.db.database import get_db
from app.models.detection import DetectionHistory
from app.models.user import User
from app.api.dependencies import get_current_user
from app.schemas.detection import DetectionResponse, DetectionHistoryResponse
from app.ml.detector import detect_objects
from app.core.storage import save_image, get_image_path, delete_image
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["画像解析"])


@router.post("/detect", response_model=DetectionResponse)
async def detect_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """画像をアップロードして物体を検出"""
    # ファイル形式のチェック
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JPGまたはPNG形式の画像をアップロードしてください"
        )
    
    # ファイルサイズのチェック
    file_content = await file.read()
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > settings.MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ファイルサイズは{settings.MAX_FILE_SIZE_MB}MB以下である必要があります"
        )
    
    try:
        # 画像サイズのチェック（大きすぎる場合はエラー）
        image = Image.open(file.file)
        width, height = image.size
        max_dimension = 10000  # 最大10000ピクセル
        
        if width > max_dimension or height > max_dimension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"画像サイズが大きすぎます。最大{max_dimension}ピクセルまで対応しています"
            )
        
        # 画像を一時ファイルに保存
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp_file:
            tmp_file.write(file_content)
            tmp_path = tmp_file.name
        
        try:
            # 物体検出
            detections, processing_time = detect_objects(tmp_path)
            
            # 画像を保存
            image_path = save_image(file_content, file.filename)
            
            # 履歴を保存
            detection_data = {
                "detections": [det.dict() for det in detections],
                "processing_time": processing_time
            }
            history = DetectionHistory(
                user_id=current_user.id,
                image_path=image_path,
                detection_results=json.dumps(detection_data, ensure_ascii=False)
            )
            db.add(history)
            db.commit()
            db.refresh(history)
            
            # 画像URLを取得（S3の場合はそのまま、ローカルの場合は相対パスを返す）
            if image_path.startswith("http"):
                image_url = image_path
            else:
                # ローカル開発環境: ファイル名のみを返す（フロントエンドで処理）
                from pathlib import Path
                image_url = f"/uploads/{Path(image_path).name}"
            
            logger.info(f"検出完了: ユーザー={current_user.username}, 検出数={len(detections)}")
            
            return DetectionResponse(
                id=history.id,
                image_url=image_url,
                detections=detections,
                processing_time=round(processing_time, 2)
            )
        finally:
            # 一時ファイルを削除
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"画像解析中にエラーが発生しました: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"画像解析中にエラーが発生しました: {str(e)}"
        )


@router.get("/history", response_model=list[DetectionHistoryResponse])
def get_history(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """解析履歴を取得"""
    histories = db.query(DetectionHistory).filter(
        DetectionHistory.user_id == current_user.id
    ).order_by(DetectionHistory.created_at.desc()).offset(skip).limit(limit).all()
    
    return histories


@router.get("/history/{history_id}", response_model=DetectionHistoryResponse)
def get_history_detail(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """特定の解析履歴の詳細を取得"""
    history = db.query(DetectionHistory).filter(
        DetectionHistory.id == history_id,
        DetectionHistory.user_id == current_user.id
    ).first()
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="履歴が見つかりません"
        )
    
    return history


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """解析履歴を削除"""
    history = db.query(DetectionHistory).filter(
        DetectionHistory.id == history_id,
        DetectionHistory.user_id == current_user.id
    ).first()
    
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="履歴が見つかりません"
        )
    
    # 画像も削除
    delete_image(history.image_path)
    
    db.delete(history)
    db.commit()
    
    logger.info(f"履歴を削除: ユーザー={current_user.username}, 履歴ID={history_id}")
    return None
