from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class DetectionBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    label: str
    confidence: float


class DetectionRequest(BaseModel):
    pass  # 画像はファイルアップロードで送信


class DetectionResponse(BaseModel):
    id: Optional[int] = None
    image_url: str
    detections: List[DetectionBox]
    processing_time: float


class DetectionHistoryResponse(BaseModel):
    id: int
    image_path: str
    detection_results: str
    created_at: datetime

    class Config:
        from_attributes = True
