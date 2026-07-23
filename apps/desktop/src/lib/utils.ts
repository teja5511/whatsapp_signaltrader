import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatStatusLabel(status: string): string {
  return (status || "").replace(/_/g, " ").toUpperCase();
}

export function getStatusBadgeVariant(status: string): "green" | "amber" | "red" | "blue" | "gray" {
  const s = (status || "").toUpperCase();
  if (["RUNNING", "HEALTHY", "CONNECTED", "EXECUTED", "FILLED", "OPEN", "ACTIVE"].includes(s)) return "green";
  if (["PAUSED", "AWAITING_CONFIRMATION", "PENDING", "DEGRADED", "CONNECTING", "WARNING", "PARTIALLY_FILLED"].includes(s)) return "amber";
  if (["EMERGENCY_STOPPED", "ERROR", "BLOCKED", "FAILED", "CANCELLED", "QUARANTINED", "STOPPED"].includes(s)) return "red";
  if (["INFO", "REPLAYING", "AUTOMATIC", "CONFIRMATION"].includes(s)) return "blue";
  return "gray";
}

export function formatDate(dateString?: string): string {
  if (!dateString) return "N/A";
  try {
    const d = new Date(dateString);
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return dateString;
  }
}
