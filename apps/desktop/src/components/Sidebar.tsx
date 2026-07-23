import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  MessageSquare,
  TrendingUp,
  Boxes,
  CheckCircle2,
  ListOrdered,
  Activity,
  Settings,
  Info,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
} from "lucide-react";
import { useUiStore } from "../stores/uiStore";
import { cn } from "../lib/utils";

const NAV_ITEMS = [
  { name: "Overview", path: "/", icon: LayoutDashboard },
  { name: "WhatsApp", path: "/whatsapp", icon: MessageSquare },
  { name: "MT5", path: "/mt5", icon: TrendingUp },
  { name: "Campaigns", path: "/campaigns", icon: Boxes },
  { name: "Confirmations", path: "/confirmations", icon: CheckCircle2 },
  { name: "Orders & Positions", path: "/positions", icon: ListOrdered },
  { name: "Events", path: "/events", icon: Activity },
  { name: "Settings", path: "/settings", icon: Settings },
  { name: "About", path: "/about", icon: Info },
];

export const Sidebar: React.FC = () => {
  const { sidebarOpen, toggleSidebar } = useUiStore();

  return (
    <aside
      className={cn(
        "bg-slate-950 border-r border-slate-800 flex flex-col justify-between transition-all duration-300 z-30 select-none",
        sidebarOpen ? "w-64" : "w-16"
      )}
    >
      <div>
        {/* Brand Header */}
        <div className="h-16 border-b border-slate-800/80 flex items-center justify-between px-4">
          <div className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded-lg bg-sky-600/20 border border-sky-500/40 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5 text-sky-400" />
            </div>
            {sidebarOpen && (
              <div className="leading-none">
                <h1 className="font-bold text-slate-100 font-mono tracking-tight text-sm">XAUUSD BOT</h1>
                <span className="text-[10px] font-mono text-sky-400 font-medium">DEMO OPERATOR</span>
              </div>
            )}
          </div>
          <button
            onClick={toggleSidebar}
            className="p-1 rounded text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
            aria-label={sidebarOpen ? "Collapse Sidebar" : "Expand Sidebar"}
          >
            {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="p-2 space-y-1">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  cn(
                    "flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-mono font-medium transition-colors",
                    isActive
                      ? "bg-sky-600/20 text-sky-400 border border-sky-500/30"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                  )
                }
                title={!sidebarOpen ? item.name : undefined}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {sidebarOpen && <span className="truncate">{item.name}</span>}
              </NavLink>
            );
          })}
        </nav>
      </div>

      {/* Footer Version Info */}
      {sidebarOpen && (
        <div className="p-4 border-t border-slate-800/80 font-mono text-[11px] text-slate-500">
          <div>Desktop v1.0.0</div>
          <div className="text-[10px] text-slate-600">Contract v1.0.0</div>
        </div>
      )}
    </aside>
  );
};
