import apiClient from './client';

export interface DetectionBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
  label: string;
  confidence: number;
}

export interface DetectionResponse {
  id?: number;
  image_url: string;
  detections: DetectionBox[];
  processing_time: number;
}

export interface DetectionHistory {
  id: number;
  image_path: string;
  detection_results: string;
  created_at: string;
}

export const detectionApi = {
  detect: async (file: File): Promise<DetectionResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/api/detect', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  },

  getHistory: async (skip: number = 0, limit: number = 20): Promise<DetectionHistory[]> => {
    const response = await apiClient.get('/api/history', {
      params: { skip, limit },
    });
    return response.data;
  },

  getHistoryDetail: async (id: number): Promise<DetectionHistory> => {
    const response = await apiClient.get(`/api/history/${id}`);
    return response.data;
  },

  deleteHistory: async (id: number): Promise<void> => {
    await apiClient.delete(`/api/history/${id}`);
  },
};
