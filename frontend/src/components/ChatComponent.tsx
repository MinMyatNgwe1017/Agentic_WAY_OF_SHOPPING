import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import { Button, Typography } from "@mui/material";
import React, { useState } from "react";

type Product = {
  product_name?: string;
  image_url?: string;
  link?: string;
  error?: string;
  status?: string;
};

export default function Chat() {
  const [message, setMessage] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
            continue;
          }

          if (obj.error) {
            setError(obj.error);
            setLoading(false);
          } else {
            setProducts((prev) => [...prev, obj]);
          }
        } catch (e) {
          console.warn("Failed to parse streamed JSON:", e, jsonStr);
        }
      }
    }
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    // reset for new search
    setProducts([]);
    setError(null);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/chat/stream", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // If you later add auth token, add it here:
          // "Authorization": `Bearer ${localStorage.getItem("token")}`,
        },
        body: JSON.stringify({
          prompt: message,
          session_id: 30, // later you can set this dynamically per user
        }),
      });

      if (!response.ok || !response.body) {
        throw new Error(`Stream request failed (${response.status})`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();

        if (value) {
          buffer += decoder.decode(value, { stream: true });

          // SSE messages are separated by a blank line "\n\n"
          const parts = buffer.split("\n\n");
          buffer = parts.pop() || "";

          for (const part of parts) {
            handleStreamPart(part);
          }
        }

        if (done) {
          break;
        }
      }

      // process any remaining final chunk
      if (buffer.trim()) {
        handleStreamPart(buffer);
      }

      setMessage("");
      setLoading(false);
    } catch (e: any) {
      setError(e?.message ?? "Something went wrong");
      setLoading(false);
    }
  };

  return (
    <div>
      <Box
        component="form"
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
          placeholder="Search a category… e.g. gaming headphones under 50 eur"
          multiline
          sx={{ display: "flex", justifyContent: "center", alignItems: "center" }}
          fullWidth
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <Button variant="contained" type="submit" disabled={loading || !message.trim()}>
          {loading ? "Searching…" : "Submit"}
        </Button>
      </Box>

      <Box sx={{ maxWidth: 900, margin: "24px auto", padding: 2 }}>
        {error && (
          <Typography sx={{ mb: 2 }} color="error">
            {error}
          </Typography>
        )}

        {products.length > 0 && (
          <Typography sx={{ mb: 2 }} variant="h6">
            Results ({products.length})
          </Typography>
        )}

        {products.map((p, idx) => (
          <Box
            key={idx}
            sx={{
              display: "flex",
              gap: 2,
              alignItems: "center",
              padding: 2,
              border: "1px solid #e0e0e0",
              borderRadius: 2,
              mb: 2,
            }}
          >
            {p.image_url ? (
              <img
                src={p.image_url}
                alt={p.product_name || "product"}
                style={{ width: 120, height: 120, objectFit: "contain" }}
              />
            ) : (
              <Box sx={{ width: 120, height: 120, border: "1px dashed #ccc" }} />
            )}

            <Box sx={{ flex: 1 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                {p.product_name || "Unnamed product"}
              </Typography>

              {p.link && (
                <Typography variant="body2">
                  <a href={p.link} target="_blank" rel="noreferrer">
                    Open product page
                  </a>
                </Typography>
              )}
            </Box>
          </Box>
        ))}

        {loading && (
          <Typography variant="body2" sx={{ mt: 2 }}>
            Streaming results… they will appear one-by-one.
          </Typography>
        )}
      </Box>
    </div>
  );
}