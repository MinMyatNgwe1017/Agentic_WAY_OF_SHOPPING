import TextField from '@mui/material/TextField';
import type { LoginInput } from '../types';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import React, { useState } from 'react';
import { login } from '../services/api';
import { useNavigate } from "react-router-dom";

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async () => {
        const loginData: LoginInput = { email, password };

        try {
            const response = await login(loginData);

            if (response?.user_id) {
                localStorage.setItem("user_id", String(response.user_id));
                localStorage.setItem("email", response.email || "");
                localStorage.setItem("fullname", response.fullname || "");
                navigate('/chat');
            }
        } catch (error: any) {
            console.error('Login failed:', error);
            alert(error?.response?.data?.detail || 'Login failed');
        }

        setEmail('');
        setPassword('');
    };

    return (
        <Stack
            component="form"
            spacing={2}
            sx={{
                width: '300px',
                margin: '0 auto',
                mt: 8
            }}
            noValidate
            autoComplete="on"
        >
            <TextField
                id="email"
                label="Email"
                variant="standard"
                onChange={(e) => setEmail(e.target.value)}
                fullWidth
                color='primary'
            />
            <TextField
                id="password"
                label="Password"
                type="password"
                variant="standard"
                onChange={(e) => setPassword(e.target.value)}
                fullWidth
                color='primary'
            />

            <Button variant="contained" onClick={handleSubmit}>Login</Button>
        </Stack>
    );
}