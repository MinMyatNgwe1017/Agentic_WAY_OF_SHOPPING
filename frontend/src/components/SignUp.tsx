import TextField from '@mui/material/TextField';
import type { SignUpInput } from '../types';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import React, { useState } from 'react';
import { creat_account } from '../services/api';

export default function Login() {
    const [email, setEmail] = useState('');
    const [fullname, setFullName] = useState('');
    const [password, setPassword] = useState('');
    const handleSubmit = async () => {
        const signupData: SignUpInput = { fullname, email, password };
        try {
            const response = await creat_account(signupData);
            alert(`message: ${response.message}`);
        } catch (error) {
            console.error('Login failed:', error);
        }

        setEmail('');
        setPassword('');
        setFullName('');
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
            <TextField id="name" label="Full Name" variant="standard" onChange={(e) => setFullName(e.target.value)} fullWidth color='primary' />
            <TextField id="email" label="Email" variant="standard" onChange={(e) => setEmail(e.target.value)} fullWidth color='primary' />
            <TextField id="password" label="Password" variant="standard" onChange={(e) => setPassword(e.target.value)} fullWidth color='primary' />

            <Button variant="contained" onClick={handleSubmit}>Sign up</Button>
        </Stack>
    );
}