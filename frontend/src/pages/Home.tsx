import { useEffect, useState } from 'react'
import { useNavigate } from "react-router-dom";
import '../App.css'
import Login from '../components/Login'
import SignUp from '../components/SignUp'
import BUTTON from '@mui/material/Button'
import { Box } from '@mui/material';

function Home() {
    const [isLogin, setIsLogin] = useState(true)
    const navigate = useNavigate();

    useEffect(() => {
        const userId = localStorage.getItem("user_id");
        if (userId) {
            navigate("/chat");
        }
    }, [navigate]);

    return (
        <Box sx={{ display: "flex", justifyContent: "center", alignItems: "center", flexDirection: "column" }}>
            {isLogin ? <Login /> : <SignUp />}

            <BUTTON onClick={() => setIsLogin(!isLogin)} style={{ marginTop: '20px' }} >
                {isLogin ? "Don't have an account? Create one" : 'Already have an account? Login'}
            </BUTTON>
        </Box>
    )
}

export default Home