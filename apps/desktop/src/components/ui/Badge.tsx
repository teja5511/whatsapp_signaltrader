import React from "react";
import { cn, getStatusBadgeVariant } from "../../lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  status?: string;
  variant?: "green" | "amber" | "red" | "blue" | "gray";
}

export const Badge: React.FC<BadgeProps> = ({ status, variant, className, children, ...props }) => {
  const resolvedVariant = variant || (status ? getStatusBadgeVariant(status) : "gray");

  const variantStyles = {
    green: "bg-emerald-950/80 text-emerald-300 border-emerald-700/50",
    amber: "bg-amber-950/80 text-amber-300 border-amber-700/50",
    red: "bg-rose-950/80 text-rose-300 border-rose-700/50",
    blue: "bg-sky-950/80 text-sky-300 border-sky-700/50",
    gray: "bg-slate-800 text-slate-300 border-slate-700",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border tracking-wide shadow-sm uppercase font-mono",
        variantStyles[resolvedVariant],
        className
      )}
      {...props}
    >
      <span
        className={cn(
          "w-1.5 h-1.5 rounded-full",
          resolvedVariant === "green" && "bg-emerald-400 animate-pulse",
          resolvedVariant === "amber" && "bg-amber-400",
          resolvedVariant === "red" && "bg-rose-400 animate-ping",
          resolvedVariant === "blue" && "bg-sky-400",
          resolvedVariant === "gray" && "bg-slate-400"
        )}
      />
      {children || status}
    </span>
  );
};
