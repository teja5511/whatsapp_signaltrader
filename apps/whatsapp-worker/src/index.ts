/**
 * WhatsApp Ingestion Worker Shell
 * Phase 2 Scaffold Version
 */
import http from "http";

const PORT = process.env.PORT || 3001;

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "healthy", service: "whatsapp-worker", timestamp: new Date().toISOString() }));
    return;
  }

  res.writeHead(404, { "Content-Type": "application/json" });
  res.end(JSON.stringify({ error: "Not Found" }));
});

server.listen(PORT, () => {
  console.log(`[WhatsApp Worker] Service shell running on http://localhost:${PORT}`);
});
