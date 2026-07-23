import React from "react";
import { cn } from "../../lib/utils";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "warning" | "outline" | "ghost";
  size?: "sm" | "md" | "lg";
}

export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "md",
  className,
  disabled,
  children,
  ...props
}) => {
  const variantStyles = {
    primary: "bg-sky-600 hover:bg-sky-500 text-white shadow-md focus:ring-sky-500",
    secondary: "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 focus:ring-slate-500",
    danger: "bg-rose-700 hover:bg-rose-600 text-white shadow-md focus:ring-rose-500",
    warning: "bg-amber-600 hover:bg-amber-500 text-white shadow-md focus:ring-amber-500",
    outline: "border border-slate-700 hover:bg-slate-800 text-slate-300 focus:ring-slate-500",
    ghost: "hover:bg-slate-800 text-slate-300 focus:ring-slate-500",
  };

  const sizeStyles = {
    sm: "px-2.5 py-1 text-xs rounded",
    md: "px-4 py-2 text-sm rounded-md",
    lg: "px-5 py-2.5 text-base rounded-lg",
  };

  return (
    <button
      className={cn(
        "inline-flex items-center justify-center font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer",
        variantStyles[variant],
        sizeStyles[size],
        className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};
