export function maskId(id?: string): string {
  if (!id) return "";
  if (id.length <= 6) return "****";
  return `${id.substring(0, 3)}****${id.substring(id.length - 3)}`;
}

export function redactSensitiveObject(obj: Record<string, any>): Record<string, any> {
  const result: Record<string, any> = {};
  for (const [key, val] of Object.entries(obj)) {
    const kLower = key.toLowerCase();
    if (
      kLower.includes("token") ||
      kLower.includes("auth") ||
      kLower.includes("cookie") ||
      kLower.includes("secret") ||
      kLower.includes("password") ||
      kLower.includes("qr")
    ) {
      result[key] = "[REDACTED]";
    } else if (typeof val === "object" && val !== null) {
      result[key] = redactSensitiveObject(val);
    } else {
      result[key] = val;
    }
  }
  return result;
}
