import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/api/auth/login', { email, password });
    return response.data;
  },
  
  register: async (email: string, username: string, password: string) => {
    const response = await api.post('/api/auth/register', { email, username, password });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};

export const projectService = {
  getProjects: async () => {
    const response = await api.get('/api/projects');
    return response.data;
  },
  
  createProject: async (name: string, description?: string, isPublic?: boolean) => {
    const response = await api.post('/api/projects', { name, description, is_public: isPublic });
    return response.data;
  },
  
  getProject: async (projectId: number) => {
    const response = await api.get(`/api/projects/${projectId}`);
    return response.data;
  },
  
  updateProject: async (projectId: number, data: any) => {
    const response = await api.put(`/api/projects/${projectId}`, data);
    return response.data;
  },
  
  deleteProject: async (projectId: number) => {
    await api.delete(`/api/projects/${projectId}`);
  },
  
  getLayers: async (projectId: number) => {
    const response = await api.get(`/api/projects/${projectId}/layers`);
    return response.data;
  },
  
  addLayer: async (projectId: number, layerData: any) => {
    const response = await api.post(`/api/projects/${projectId}/layers`, layerData);
    return response.data;
  },
};

export const featureService = {
  getFeatures: async (layerId: number) => {
    const response = await api.get(`/api/features/layer/${layerId}`);
    return response.data;
  },
  
  createFeature: async (layerId: number, geometry: any, properties?: any) => {
    const response = await api.post(`/api/features/layer/${layerId}`, { geometry, properties });
    return response.data;
  },
  
  updateFeature: async (featureId: number, geometry?: any, properties?: any) => {
    const response = await api.put(`/api/features/${featureId}`, { geometry, properties });
    return response.data;
  },
  
  deleteFeature: async (featureId: number) => {
    await api.delete(`/api/features/${featureId}`);
  },
  
  lockFeature: async (featureId: number) => {
    const response = await api.post(`/api/features/${featureId}/lock`);
    return response.data;
  },
  
  unlockFeature: async (featureId: number) => {
    const response = await api.post(`/api/features/${featureId}/unlock`);
    return response.data;
  },
  
  getComments: async (featureId: number) => {
    const response = await api.get(`/api/features/${featureId}/comments`);
    return response.data;
  },
  
  addComment: async (featureId: number, content: string) => {
    const response = await api.post(`/api/features/${featureId}/comments`, { content });
    return response.data;
  },
};

export const geoprocessService = {
  measureDistance: async (startLat: number, startLon: number, endLat: number, endLon: number) => {
    const response = await api.get('/api/geoprocess/measure/distance', {
      params: { start_lat: startLat, start_lon: startLon, end_lat: endLat, end_lon: endLon }
    });
    return response.data;
  },
  
  buffer: async (layerId: number, distance: number) => {
    const response = await api.post('/api/geoprocess/buffer', { layer_id: layerId, distance });
    return response.data;
  },
};

export default api;
