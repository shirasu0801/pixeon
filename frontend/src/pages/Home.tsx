import { useState, useRef } from 'react';
import {
  Container,
  Paper,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  Card,
  CardContent,
  CardMedia,
} from '@mui/material';
import { PhotoCamera, CloudUpload } from '@mui/icons-material';
import { detectionApi } from '../api/detection';
import type { DetectionResponse, DetectionBox } from '../api/detection';

export const Home = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<DetectionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('ファイルサイズは10MB以下である必要があります');
        return;
      }
      if (!['image/jpeg', 'image/png', 'image/jpg'].includes(selectedFile.type)) {
        setError('JPGまたはPNG形式の画像を選択してください');
        return;
      }
      setFile(selectedFile);
      setError('');
      setResult(null);
      
      // プレビューを表示
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleDetect = async () => {
    if (!file) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const detectionResult = await detectionApi.detect(file);
      setResult(detectionResult);
      drawDetections(detectionResult);
    } catch (err: any) {
      setError(err.response?.data?.detail || '画像解析中にエラーが発生しました');
    } finally {
      setLoading(false);
    }
  };

  const drawDetections = (detection: DetectionResponse) => {
    if (!canvasRef.current || !preview) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = () => {
      // キャンバスサイズを画像に合わせる（最大幅800pxに制限）
      const maxWidth = 800;
      let width = img.width;
      let height = img.height;
      
      if (width > maxWidth) {
        height = (height * maxWidth) / width;
        width = maxWidth;
      }
      
      canvas.width = width;
      canvas.height = height;
      ctx.drawImage(img, 0, 0, width, height);

      // スケールファクターを計算
      const scaleX = width / img.width;
      const scaleY = height / img.height;

      // 検出結果を描画
      detection.detections.forEach((box: DetectionBox) => {
        // スケールされた座標を計算
        const x1 = box.x1 * scaleX;
        const y1 = box.y1 * scaleY;
        const x2 = box.x2 * scaleX;
        const y2 = box.y2 * scaleY;

        // バウンディングボックスを描画
        ctx.strokeStyle = '#00ff00';
        ctx.lineWidth = 3;
        ctx.strokeRect(x1, y1, x2 - x1, y2 - y1);

        // ラベルと信頼度を描画
        ctx.fillStyle = '#00ff00';
        ctx.font = `${Math.max(12, width / 40)}px Arial`;
        const labelText = `${box.label} (${box.confidence}%)`;
        const textMetrics = ctx.measureText(labelText);
        ctx.fillRect(x1, y1 - 25, textMetrics.width + 10, 25);
        ctx.fillStyle = '#000000';
        ctx.fillText(labelText, x1 + 5, y1 - 5);
      });
    };
    img.src = preview;
  };

  const handleCameraClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom align="center">
          画像認識アプリ
        </Typography>
        <Typography variant="body1" align="center" color="text.secondary" gutterBottom>
          画像をアップロードして、AIが物体を検出します
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Paper elevation={3} sx={{ p: 4, mb: 4 }}>
        <Box display="flex" flexDirection="column" alignItems="center" gap={2}>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/png,image/jpg"
            onChange={handleFileSelect}
            style={{ display: 'none' }}
          />

          <Button
            variant="contained"
            component="label"
            startIcon={<CloudUpload />}
            size="large"
            onClick={handleCameraClick}
          >
            画像を選択
          </Button>

          {preview && (
            <Box mt={2}>
              <Card>
                <CardMedia
                  component="img"
                  image={preview}
                  alt="プレビュー"
                  sx={{ maxHeight: 400, objectFit: 'contain' }}
                />
                <CardContent>
                  <Button
                    variant="contained"
                    fullWidth
                    onClick={handleDetect}
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <PhotoCamera />}
                  >
                    {loading ? '解析中...' : '物体を検出'}
                  </Button>
                </CardContent>
              </Card>
            </Box>
          )}

          {result && (
            <Box mt={2} width="100%">
              <Typography variant="h6" gutterBottom>
                検出結果
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                処理時間: {result.processing_time}秒
              </Typography>
              <Box mt={2} display="flex" justifyContent="center">
                <canvas
                  ref={canvasRef}
                  style={{ maxWidth: '100%', height: 'auto', border: '1px solid #ccc', borderRadius: '4px' }}
                />
              </Box>
              <Box mt={2}>
                <Typography variant="h6">検出された物体:</Typography>
                {result.detections.map((det, index) => (
                  <Typography key={index} variant="body1">
                    {det.label}: {det.confidence}%
                  </Typography>
                ))}
              </Box>
            </Box>
          )}
        </Box>
      </Paper>
    </Container>
  );
};
