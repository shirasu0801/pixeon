import time
from typing import List
from pathlib import Path
from ultralytics import YOLO
from app.schemas.detection import DetectionBox
import logging

logger = logging.getLogger(__name__)

# YOLOv8モデルをロード（初回のみ）
_model = None


def get_model():
    """YOLOv8モデルを取得（シングルトン）"""
    global _model
    if _model is None:
        try:
            # YOLOv8n（nano）モデルを使用（軽量で高速）
            _model = YOLO("yolov8n.pt")
            logger.info("YOLOv8モデルをロードしました")
        except Exception as e:
            logger.error(f"モデルのロードに失敗しました: {e}")
            raise
    return _model


def detect_objects(image_path: str) -> tuple[List[DetectionBox], float]:
    """
    画像内の物体を検出
    
    Args:
        image_path: 画像ファイルのパス
        
    Returns:
        (検出結果のリスト, 処理時間)
    """
    start_time = time.time()
    
    try:
        model = get_model()
        results = model(image_path)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # バウンディングボックスの座標を取得
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                # クラス名と信頼度を取得
                cls = int(box.cls[0].cpu().numpy())
                confidence = float(box.conf[0].cpu().numpy())
                label = model.names[cls]
                
                detections.append(DetectionBox(
                    x1=float(x1),
                    y1=float(y1),
                    x2=float(x2),
                    y2=float(y2),
                    label=label,
                    confidence=round(confidence * 100, 2)  # パーセンテージに変換
                ))
        
        processing_time = time.time() - start_time
        logger.info(f"検出完了: {len(detections)}個の物体を検出、処理時間: {processing_time:.2f}秒")
        
        return detections, processing_time
        
    except Exception as e:
        logger.error(f"物体検出中にエラーが発生しました: {e}")
        raise
