import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import { Button } from '@mui/material';
import React, { useState } from 'react';
import { chat } from '../services/api';

export default function Chat() {
    const [message, setMessage] = useState("");

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        const response = await chat({ prompt: message });
        console.log("Message submitted:", response);
        setMessage("");
    }
    return (
        <div>
            <Box component="form"
                noValidate
                autoComplete="off"
                sx={{
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    flexDirection: "row",
                    gap: 2,
                    marginTop: 2,
                    width: "100%",
                    minWidth: { xs: "100%", sm: "300px", md: "500px" },
                }}
                onSubmit={handleSubmit}
            >

                <TextField
                    id="outlined-textarea"
                    placeholder="Write something..."
                    multiline
                    sx={{ display: "flex", justifyContent: "center", alignItems: "center" }}
                    fullWidth
                    onChange={(e) => setMessage(e.target.value)}
                />
                <Button variant="contained" type="submit">Submit</Button>
            </Box>
        </div>
    );
}