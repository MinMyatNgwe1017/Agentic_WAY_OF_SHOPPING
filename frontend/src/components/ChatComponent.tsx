import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import { Button, Typography, Paper, Divider } from "@mui/material";

type Product = {
  product_name?: string;
  image_url?: string;
  link?: string;
  error?: string;
  status?: string;
  type?: string;
  message?: string;
  question?: string;
  price?: number;
  recom?: string;
};

type ChatMessage = {
  sender: "user" | "agent";
  text: string;
};

export default function Chat() {
  const [message, setMessage] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [currentStatus, setCurrentStatus] = useState<string | null>(null);
  const navigate = useNavigate();
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const hasResults = products.length > 0;

  useEffect(() => {
    const userId = localStorage.getItem("user_id");
    if (!userId) navigate("/");
  }, [navigate]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  const handleStreamPart = (part: string) => {
    const lines = part.split("\n");
    for (const line of lines) {
      if (line.startsWith("data:")) {
        const jsonStr = line.replace("data:", "").trim();
        if (!jsonStr) continue;

        try {
          const obj = JSON.parse(jsonStr) as Product;

          if (obj.status === "done") {
            setLoading(false);
            setCurrentStatus(null);
            return;
          }

          if (obj.status === "need_user") {
            setChatHistory((prev) => [...prev, { sender: "agent", text: obj.question || "Details please?" }]);
            setCurrentStatus(null);
            setLoading(false);
            return;
          }

          if (obj.type === "status") {
            setCurrentStatus(obj.message || "Processing...");
            return;
          }
          if (obj.error) {
            setChatHistory((prev) => [...prev, { sender: "agent", text: obj.error! }]);
          } else {
            setProducts((prev) => [...prev, obj]);
          }
        } catch (e) {
          console.warn("Stream parse error:", e);
        }
      }
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!message.trim()) return;

    const userId = localStorage.getItem("user_id");
    setChatHistory((prev) => [...prev, { sender: "user", text: message }]);

    const currentMsg = message;
    setMessage("");
    setProducts([]);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: currentMsg, session_id: Number(userId) }),
      });

      if (!response.body) return;
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (value) {
          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split("\n\n");
          buffer = parts.pop() || "";
          for (const part of parts) handleStreamPart(part);
        }
        if (done) break;
      }
      if (buffer.trim()) handleStreamPart(buffer);
    } catch (e) {
      setChatHistory((prev) => [...prev, { sender: "agent", text: "Connection error." }]);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate("/");
  };
  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "100%", width: "100%", overflow: "hidden" }}>

      <Paper elevation={1} sx={{ p: 2, display: "flex", justifyContent: "space-between", alignItems: "center", borderRadius: 0, zIndex: 10, }}>
        <Typography variant="body2" sx={{ fontWeight: 500 }}>
          {localStorage.getItem("fullname") || "User"}
        </Typography>
        <Button size="small" variant="outlined" color="error" onClick={handleLogout}>Logout</Button>
      </Paper>

      <Box sx={{ display: "flex", flex: 1, overflow: "hidden" }}>

        {hasResults && (
          <Box sx={{ flex: 1, p: 3, overflowY: "auto", borderRight: "1px solid #e0e0e0" }}>
            <Typography variant="h5" sx={{ mb: 3, fontWeight: 600 }}>
              Recommended for you
            </Typography>
            <Box sx={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: 2 }}>
              {products.map((p, idx) => (
                <Paper key={idx} variant="outlined" sx={{ p: 2, borderRadius: 2, display: "flex", flexDirection: "column", gap: 1 }}>
                  {p.image_url ? (
                    <img src={p.image_url} alt="product" style={{ width: "100%", height: 180, objectFit: "contain" }} />
                  ) : (
                    <Box sx={{ height: 180, bgcolor: "#eee", borderRadius: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>No Image</Box>
                  )}

                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mt: 1, lineHeight: 1.2 }}>
                    {p.product_name}
                  </Typography>

                  <Typography variant="h6" color="primary.main" sx={{ fontWeight: 700 }}>
                    ${p.price}
                  </Typography>

                  {p.recom && (
                    <Typography variant="body2" color="text.secondary" sx={{ fontStyle: "italic", mb: 1 }}>
                      {p.recom}
                    </Typography>
                  )}

                  <Button
                    variant="contained"
                    href={p.link || "#"}
                    target={p.link ? "_blank" : undefined}
                    disabled={!p.link}
                    fullWidth
                    sx={{ mt: "auto", textTransform: "none" }}
                  >
                    View Deal
                  </Button>
                </Paper>
              ))}
            </Box>
          </Box>
        )}

        <Box sx={{
          flex: hasResults ? "0 0 400px" : 1,
          display: "flex",
          flexDirection: "column",
          width: "100%",
          minWidth: 0,
          height: "100%",
          overflow: "hidden"
        }}>

          <Box sx={{
            flex: 1,
            overflowY: "auto",
            p: 3,
            display: "flex",
            flexDirection: "column",
            minHeight: 0,
            gap: 2,
            "&::-webkit-scrollbar": { width: "5px" },
            "&::-webkit-scrollbar-thumb": { borderRadius: "10px" },
            background: "#151414"
          }}>
            {chatHistory.length === 0 && (
              <Box sx={{ textAlign: "center", mt: 10, color: "#e6e3e3" }}>
                <Typography variant="h5">How can I help you find something today?</Typography>
              </Box>
            )}
            {chatHistory.map((msg, idx) => (
              <Box key={idx} sx={{ display: "flex", justifyContent: msg.sender === "user" ? "flex-end" : "flex-start" }}>
                <Box sx={{
                  maxWidth: "85%",
                  p: 2,
                  borderRadius: msg.sender === "user" ? "20px 20px 4px 20px" : "20px 20px 20px 4px",
                  bgcolor: msg.sender === "user" ? "#1976d2" : "#f0f2f5",
                  color: msg.sender === "user" ? "white" : "#1c1e21",
                  boxShadow: "0 2px 4px rgba(0,0,0,0.05)"
                }}>
                  <Typography variant="body1">{msg.text}</Typography>
                </Box>
              </Box>
            ))}

            {currentStatus && (
              <Box sx={{ ml: 1, mb: 2 }}>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 1,
                    bgcolor: "rgba(255, 255, 255, 0.05)",
                    color: "#aaa",
                    fontSize: "0.85rem",
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 1,
                    borderRadius: 2,
                    border: "1px solid #444"
                  }}
                >
                  <Box
                    sx={{
                      width: 8, height: 8, bgcolor: "#1976d2", borderRadius: "50%",
                      animation: "pulse 1.5s infinite"
                    }}
                  />
                  {currentStatus}
                </Paper>
              </Box>
            )}

            {loading && !currentStatus && (
              <Typography variant="caption" sx={{ color: "#666", fontStyle: "italic", ml: 1 }}>
                AI is thinking...
              </Typography>
            )}
            <div ref={chatEndRef} />
          </Box>

          <Divider />
          <Box component="form" onSubmit={handleSubmit} sx={{ p: 2, }}>
            <TextField
              fullWidth
              multiline
              rows={3}
              placeholder="Type your request (e.g., 'I want a laptop under 500€')"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              sx={{
                "& .MuiOutlinedInput-root": { borderRadius: 3, bgcolor: "#ffffff" },
                mb: 1
              }}
            />
            <Box sx={{ display: "flex", justifyContent: "flex-end" }}>
              <Button type="submit" variant="contained" disabled={loading || !message.trim()} sx={{ borderRadius: 5, px: 4 }}>
                Send
              </Button>
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}