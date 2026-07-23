import React from "react";
import { Outlet } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Sidebar } from "../components/Sidebar";
import { Topbar } from "../components/Topbar";
import { SafetyBanner } from "../components/SafetyBanner";
import { ConfirmDialog } from "../components/ConfirmDialog";
import { apiClient } from "../api/apiClient";
import { globalEventClient } from "../realtime/eventClient";

export const DashboardLayout: React.FC = () => {
  const { data: status, isError } = useQuery({
    queryKey: ["systemStatus"],
    queryFn: () => apiClient.getSystemStatus(),
    refetchInterval: 3000,
  });

  const realtimeStatus = globalEventClient.getStatus();

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-950 text-slate-100 font-sans antialiased selection:bg-sky-500 selection:text-white">
      {/* Sidebar Navigation */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex flex-col flex-1 min-w-0 h-full">
        {/* Persistent Top Bar */}
        <Topbar
          systemStatus={status}
          realtimeStatus={realtimeStatus}
          fastApiHealthy={!isError}
        />

        {/* Safety & Warning Banner */}
        <SafetyBanner systemStatus={status} fastApiOffline={isError} />

        {/* Scrollable Page Content */}
        <main className="flex-1 overflow-y-auto p-6 space-y-6">
          <Outlet />
        </main>
      </div>

      {/* Global Dangerous Action Confirmation Modal */}
      <ConfirmDialog />
    </div>
  );
};
