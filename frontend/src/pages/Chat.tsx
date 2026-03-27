import { Box } from '@mui/material'
import ChatComponent from '../components/ChatComponent'


export default function Chat() {
    return (
        <Box sx={{
            width: "100%",
            height: "100vh",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden"
        }}>
            <ChatComponent />
        </Box>
    )
}
