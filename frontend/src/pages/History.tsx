import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Card,
  CardContent,
  CardMedia,
  Grid,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import { Delete } from '@mui/icons-material';
import { detectionApi } from '../api/detection';
import type { DetectionHistory } from '../api/detection';

export const History = () => {
  const [histories, setHistories] = useState<DetectionHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setLoading(true);
      const data = await detectionApi.getHistory();
      setHistories(data);
    } catch (err: any) {
      setError('履歴の取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('この履歴を削除しますか？')) return;

    try {
      await detectionApi.deleteHistory(id);
      setHistories(histories.filter((h) => h.id !== id));
    } catch (err: any) {
      setError('削除に失敗しました');
    }
  };

  if (loading) {
    return (
      <Container>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          解析履歴
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {histories.length === 0 ? (
        <Typography variant="body1" color="text.secondary" align="center">
          履歴がありません
        </Typography>
      ) : (
        <Grid container spacing={3}>
          {histories.map((history) => {
            const results = JSON.parse(history.detection_results);
            return (
              <Grid item xs={12} sm={6} md={4} key={history.id}>
                <Card>
                  <CardMedia
                    component="img"
                    image={history.image_path.startsWith('http') 
                      ? history.image_path 
                      : `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}${history.image_path}`}
                    alt="解析画像"
                    sx={{ height: 200, objectFit: 'cover' }}
                  />
                  <CardContent>
                    <Typography variant="body2" color="text.secondary">
                      {new Date(history.created_at).toLocaleString('ja-JP')}
                    </Typography>
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      検出数: {results.detections?.length || 0}
                    </Typography>
                    <Button
                      size="small"
                      color="error"
                      startIcon={<Delete />}
                      onClick={() => handleDelete(history.id)}
                      sx={{ mt: 1 }}
                    >
                      削除
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}
    </Container>
  );
};
