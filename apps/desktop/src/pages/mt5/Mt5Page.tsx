import React from "react";
import { useQuery } from "@tanstack/react-query";
import { apiClient } from "../../api/apiClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { TrendingUp, RefreshCw, Power, Lock, CheckCircle2 } from "lucide-react";

export const Mt5Page: React.FC = () => {
  const { data: status, refetch: refetchStatus } = useQuery({
    queryKey: ["mt5Status"],
    queryFn: () => apiClient.getMt5Status().catch(() => ({ initialized: false, adapter_mode: "fake" })),
    refetchInterval: 5000,
  });

  const { data: account } = useQuery({
    queryKey: ["mt5Account"],
    queryFn: () => apiClient.getMt5Account().catch(() => null),
    refetchInterval: 5000,
  });

  const { data: symbol } = useQuery({
    queryKey: ["mt5Symbol"],
    queryFn: () => apiClient.getMt5Symbol().catch(() => null),
    refetchInterval: 5000,
  });

  const { data: batches } = useQuery({
    queryKey: ["executionBatches"],
    queryFn: () => apiClient.getExecutionBatches().catch(() => []),
    refetchInterval: 5000,
  });

  const handleInitialize = async () => {
    await apiClient.initializeMt5();
    refetchStatus();
  };

  const handleShutdown = async () => {
    await apiClient.shutdownMt5();
    refetchStatus();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold font-mono text-slate-100">MetaTrader 5 Adapter & Account Monitor</h1>
          <p className="text-xs text-slate-400 mt-1">Exness MT5 Hedging Account status, XAUUSD symbol specifications, and batch queue execution.</p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => refetchStatus()} className="gap-2 font-mono">
          <RefreshCw className="w-3.5 h-3.5" /> Refresh Status
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Adapter Status & Controls */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2 text-sky-400">
                <TrendingUp className="w-4 h-4" /> MT5 IPC Adapter
              </CardTitle>
              <CardDescription>Python `MetaTrader5` IPC Terminal Binding</CardDescription>
            </div>
            <Badge status={status?.initialized ? "INITIALIZED" : "UNINITIALIZED"} />
          </CardHeader>

          <div className="space-y-3 font-mono text-xs border-t border-slate-800 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Adapter Mode:</span>
              <span className="text-slate-200 uppercase font-bold">{status?.adapter_mode || "fake"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Health State:</span>
              <span className="text-emerald-400 font-bold">{status?.health_state || "READY"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Environment:</span>
              <span className="text-emerald-300 font-bold">DEMO ONLY</span>
            </div>
          </div>

          <div className="mt-6 flex gap-3 border-t border-slate-800 pt-4">
            {status?.initialized ? (
              <Button variant="secondary" size="sm" onClick={handleShutdown} className="w-full gap-2">
                <Power className="w-4 h-4 text-rose-400" /> Shutdown IPC
              </Button>
            ) : (
              <Button variant="primary" size="sm" onClick={handleInitialize} className="w-full gap-2">
                <Power className="w-4 h-4 text-emerald-400" /> Initialize IPC
              </Button>
            )}
          </div>
        </Card>

        {/* Account Info */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2 text-emerald-400">
                <Lock className="w-4 h-4" /> Account Information
              </CardTitle>
              <CardDescription>Exness Demo Account Specifications</CardDescription>
            </div>
            <Badge status="DEMO" variant="green" />
          </CardHeader>

          <div className="space-y-3 font-mono text-xs border-t border-slate-800 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Login Masked:</span>
              <span className="text-slate-200">{account?.login_masked || "****5678"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Server:</span>
              <span className="text-slate-200">{account?.server || "Exness-MT5Demo"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Balance:</span>
              <span className="text-emerald-400 font-bold">${account?.balance?.toFixed(2) || "10000.00"} USD</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Equity:</span>
              <span className="text-emerald-400 font-bold">${account?.equity?.toFixed(2) || "10000.00"} USD</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Leverage / Mode:</span>
              <span className="text-slate-200">1:{account?.leverage || 500} (Hedging)</span>
            </div>
          </div>
        </Card>

        {/* Symbol Specification */}
        <Card>
          <CardHeader>
            <div>
              <CardTitle className="flex items-center gap-2 text-indigo-400">
                <CheckCircle2 className="w-4 h-4" /> Symbol Specifications
              </CardTitle>
              <CardDescription>XAUUSD Contract Trading Rules</CardDescription>
            </div>
            <Badge status="XAUUSD" variant="blue" />
          </CardHeader>

          <div className="space-y-3 font-mono text-xs border-t border-slate-800 pt-4">
            <div className="flex justify-between">
              <span className="text-slate-400">Canonical Symbol:</span>
              <span className="text-slate-200 font-bold">XAUUSD</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Broker Symbol:</span>
              <span className="text-slate-200">{symbol?.broker_symbol || "XAUUSDm"}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Digits / Point:</span>
              <span className="text-slate-200">{symbol?.digits || 2} / {symbol?.point || 0.01}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Volume Min/Max/Step:</span>
              <span className="text-slate-200">0.01 / 2.00 / 0.01</span>
            </div>
          </div>
        </Card>
      </div>

      {/* Execution Batches */}
      <Card>
        <CardHeader>
          <CardTitle className="text-slate-200">MT5 Execution Batch Queue</CardTitle>
          <CardDescription>Durable single-writer execution queue processing limit order submissions.</CardDescription>
        </CardHeader>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-slate-950 text-slate-400 uppercase text-[10px]">
              <tr>
                <th className="p-3">Batch ID</th>
                <th className="p-3">Campaign ID</th>
                <th className="p-3">Status</th>
                <th className="p-3">Total Jobs</th>
                <th className="p-3">Completed</th>
                <th className="p-3">Failed</th>
                <th className="p-3">Created</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {(batches || []).length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-4 text-center text-slate-500">
                    No execution batches queued.
                  </td>
                </tr>
              ) : (
                (batches || []).map((b: any) => (
                  <tr key={b.id} className="hover:bg-slate-800/40">
                    <td className="p-3 font-semibold text-slate-200">{b.id.substring(0, 8)}...</td>
                    <td className="p-3 text-sky-400">{b.campaign_id?.substring(0, 8)}...</td>
                    <td className="p-3"><Badge status={b.status} /></td>
                    <td className="p-3 text-slate-300">{b.total_jobs}</td>
                    <td className="p-3 text-emerald-400">{b.completed_jobs}</td>
                    <td className="p-3 text-rose-400">{b.failed_jobs}</td>
                    <td className="p-3 text-slate-400">{new Date(b.created_at).toLocaleTimeString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
