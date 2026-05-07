import TextField from '@mui/material/TextField';
import type { SignUpInput } from '../types';
import Stack from '@mui/material/Stack';
import Button from '@mui/material/Button';
import React, { useState } from 'react';
import { creat_account } from '../services/api';
import { useNavigate, Link } from "react-router-dom";

export default function SignUp() {
    const [fullname, setFullName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
        e.preventDefault(); 

        const signupData: SignUpInput = { fullname, email, password };
        console.log("Sending to backend:", signupData); 

        try {
            const response = await creat_account(signupData);

            if (response?.user_id) {
                localStorage.setItem("user_id", String(response.user_id));
                localStorage.setItem("email", response.email || "");
                localStorage.setItem("fullname", response.fullname || "");
                navigate('/chat');
            }
        } catch (error: any) {
            console.error('Signup failed:', error);
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
            <TextField
                id="name"
                label="Full Name"
                variant="standard"
                value={fullname}
                onChange={(e) => setFullName(e.target.value)}
                fullWidth
                sx={{ color: '#fff', backgroundColor: '#fff', }}
            />
            <TextField
                id="email"
                label="Email"
                variant="standard"
                value={email} 
                onChange={(e) => setEmail(e.target.value)}
                fullWidth
                sx={{ color: '#fff', backgroundColor: '#fff', }}
            />
            <TextField
                id="password"
                label="Password"
                type="password"
                variant="standard"
                value={password} 
                onChange={(e) => setPassword(e.target.value)}
                fullWidth
                sx={{ color: '#fff', backgroundColor: '#fff' }}
            />

            <Button variant="contained" onClick={handleSubmit} type="button">
                Sign up
            </Button>

            <Button component={Link} to="/login" sx={{ mt: 2 }}>
                ALREADY HAVE AN ACCOUNT? LOGIN
            </Button>
        </Stack>
    );
}