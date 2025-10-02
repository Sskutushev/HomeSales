import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api', // Use environment variable or local fallback
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;