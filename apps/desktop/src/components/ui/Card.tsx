import React from "react";
import { cn } from "../../lib/utils";

export const Card: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => {
  return (
    <div
      className={cn(
        "bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-sm",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export const CardHeader: React.FC<React.HTMLAttributes<HTMLDivElement>> = ({ className, children, ...props }) => {
  return <div className={cn("mb-4 flex items-center justify-between", className)} {...props}>{children}</div>;
};

export const CardTitle: React.FC<React.HTMLAttributes<HTMLHeadingElement>> = ({ className, children, ...props }) => {
  return <h3 className={cn("text-base font-semibold text-slate-100 font-mono tracking-tight", className)} {...props}>{children}</h3>;
};

export const CardDescription: React.FC<React.HTMLAttributes<HTMLParagraphElement>> = ({ className, children, ...props }) => {
  return <p className={cn("text-xs text-slate-400 mt-0.5", className)} {...props}>{children}</p>;
};
