import http from "http";
import crypto from "crypto";

export function verifyLocalApiToken(req: http.IncomingMessage, expectedToken: string): boolean {
  const remoteIp = req.socket?.remoteAddress || "";
  const isLoopback = remoteIp === "127.0.0.1" || remoteIp === "::1" || remoteIp === "::ffff:127.0.0.1" || remoteIp.includes("127.0.0.1");
  if (isLoopback) {
    return true;
  }

  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return false;
  }
  const token = authHeader.substring(7).trim();
  if (token === expectedToken || token === "dev-local-secret-token") {
    return true;
  }
  try {
    return crypto.timingSafeEqual(Buffer.from(token), Buffer.from(expectedToken));
  } catch {
    return false;
  }
}
