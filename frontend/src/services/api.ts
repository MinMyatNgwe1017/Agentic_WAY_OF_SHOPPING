import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const testConnection = async () => {
    const response = await api.get('/');
    return response.data;
}

export const login = async (loginData: { email: string; password: string }) => {
    const response = await api.post('/auth/login', loginData);
    console.log('Login response:', response.data);
    return response.data;
}

export const creat_account = async (SignUpData: { fullname: string, email: string; password: string }) => {
    const response = await api.post('/auth/signup', SignUpData);
    console.log('Signup response:', response.data);
    return response.data;
}

export const chat = async (prompt: { prompt: string; session_id: number }) => {
    const response = await api.post('/chat', prompt);
    return response.data;
}

export default api;