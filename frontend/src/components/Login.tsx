import TextField from '@mui/material/TextField';
import type { LoginInput } from '../types';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import React, { useState } from 'react';
import { login } from '../services/api';

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const handleSubmit = async () => {
        const loginData: LoginInput = { email, password };
        try {
            const response = await login(loginData);
            alert(`Login successful: ${response.message}`);
        } catch (error) {
            console.error('Login failed:', error);
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
            <TextField id="email" label="Email" variant="standard" onChange={(e) => setEmail(e.target.value)} fullWidth color='primary' />
            <TextField id="password" label="Password" variant="standard" onChange={(e) => setPassword(e.target.value)} fullWidth color='primary' />

            <Button variant="contained" onClick={handleSubmit}>Login</Button>
        </Stack>
    );
}