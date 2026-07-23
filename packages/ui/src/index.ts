// Shared UI Component Shells & Design Tokens

export const DESIGN_TOKENS = {
  colors: {
    primary: "#0284c7",
    success: "#16a34a",
    warning: "#d97706",
    danger: "#dc2626",
    backgroundDark: "#0f172a",
    cardDark: "#1e293b",
    textLight: "#f8fafc"
  }
};

export interface StatusBadgeProps {
  status: string;
  isDemo?: boolean;
}

export function formatStatusLabel(status: string): string {
  return status.replace(/_/g, " ").toUpperCase();
}
