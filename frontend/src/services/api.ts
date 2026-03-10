
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const testConnection = async () => {
    const response = await api.get('/test');
    return response.data;
}

export const login = async (loginData: { email: string; password: string }) => {
    const response = await api.post('/auth/login', loginData);
    console.log('Login response:', response.data);
    return response.data;
}
export const creat_account = async (SignUpData: { fullname: string, email: string; password: string, }) => {
    const response = await api.post('/auth/signup', SignUpData);
    console.log('Login response:', response.data);
    return response.data;
}

export const chat = async (prompt: { prompt: string }) => {
    const response = await api.post('/chat', prompt);
    return response.data;
}