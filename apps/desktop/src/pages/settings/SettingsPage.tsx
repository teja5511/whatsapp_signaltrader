import React, { useState, useEffect } from "react";
import { secureTokenSet, secureTokenExists, secureTokenClear } from "../../api/tauriClient";
import { Card, CardHeader, CardTitle, CardDescription } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import { Button } from "../../components/ui/Button";
import { useUiStore } from "../../stores/uiStore";
import { Settings, Lock, Shield, Check, Trash2, Key } from "lucide-react";

export const SettingsPage: React.FC = () => {
  const { theme, setTheme, mockMode, setMockMode } = useUiStore();
  const [tokenInput, setTokenInput] = useState("");
  const [hasToken, setHasToken] = useState(false);
  const [savedMsg, setSavedMsg] = useState<string | null>(null);

  useEffect(() => {
    secureTokenExists().then((exists) => setHasToken(exists));
  }, []);

  const handleSaveToken = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tokenInput.trim()) return;
    await secureTokenSet(tokenInput.trim());
    setHasToken(true);
    setTokenInput("");
    setSavedMsg("Local API Bearer token stored securely in Rust memory store.");
    setTimeout(() => setSavedMsg(null), 4000);
  };

  const handleClearToken = async () => {
    await secureTokenClear();
    setHasToken(false);
    setSavedMsg("Token cleared.");
    setTimeout(() => setSavedMsg(null), 4000);
  };

  return (
    <div className="space-y-6 font-mono max-w-4xl">
      <div>
        <h1 className="text-xl font-bold text-slate-100 font-mono">Desktop Dashboard Settings</h1>
        <p className="text-xs text-slate-400 mt-1">Configure secure local token authentication, connection URLs, and trading safety defaults.</p>
      </div>

      {savedMsg && (
        <div className="p-3 rounded bg-emerald-950/80 border border-emerald-700/80 text-emerald-300 text-xs flex items-center gap-2">
          <Check className="w-4 h-4" /> {savedMsg}
        </div>
      )}

      {/* Secure Token Configuration */}
      <Card>
        <CardHeader>
          <div>
            <CardTitle className="text-sky-400 flex items-center gap-2">
              <Key className="w-4 h-4" /> Local API Bearer Token Authentication
            </CardTitle>
            <CardDescription>
              Stored in Rust secure memory store. Never saved in localStorage, sessionStorage, URLs, or plain JSON.
            </CardDescription>
          </div>
          <Badge status={hasToken ? "CONFIGURED" : "NOT_SET"} variant={hasToken ? "green" : "red"} />
        </CardHeader>

        <form onSubmit={handleSaveToken} className="space-y-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Set Local API Token (<code className="text-sky-400">LOCAL_API_TOKEN</code>)
            </label>
            <input
              type="password"
              value={tokenInput}
              onChange={(e) => setTokenInput(e.target.value)}
              placeholder={hasToken ? "••••••••••••••••" : "Enter local secret token..."}
              className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-sky-500 font-mono"
            />
          </div>

          <div className="flex items-center gap-3">
            <Button type="submit" variant="primary" size="sm" disabled={!tokenInput.trim()}>
              Save Secure Token
            </Button>
            {hasToken && (
              <Button type="button" variant="danger" size="sm" onClick={handleClearToken} className="gap-1.5">
                <Trash2 className="w-3.5 h-3.5" /> Clear Token
              </Button>
            )}
          </div>
        </form>
      </Card>

      {/* API Connections & Loopback Safety */}
      <Card>
        <CardHeader>
          <CardTitle className="text-emerald-400 flex items-center gap-2">
            <Lock className="w-4 h-4" /> Connection URLs (Loopback Only Default)
          </CardTitle>
        </CardHeader>

        <div className="space-y-4 text-xs font-mono">
          <div>
            <label className="block text-slate-400 mb-1">FastAPI Orchestrator URL:</label>
            <input
              type="text"
              readOnly
              value="http://127.0.0.1:8000"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-slate-300"
            />
          </div>
          <div>
            <label className="block text-slate-400 mb-1">WhatsApp Baileys Worker URL:</label>
            <input
              type="text"
              readOnly
              value="http://127.0.0.1:8010"
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded text-slate-300"
            />
          </div>
        </div>
      </Card>

      {/* Interface Preferences */}
      <Card>
        <CardHeader>
          <CardTitle className="text-slate-200">Interface & Mock Mode</CardTitle>
        </CardHeader>

        <div className="space-y-4 text-xs font-mono">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-slate-200 block font-bold">Mock Mode (VITE_DESKTOP_MOCK_MODE)</span>
              <span className="text-slate-400">Use local mock fixtures for UI testing without backend servers.</span>
            </div>
            <Button
              variant={mockMode ? "warning" : "secondary"}
              size="sm"
              onClick={() => setMockMode(!mockMode)}
            >
              {mockMode ? "MOCK MODE ON" : "MOCK MODE OFF"}
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
};
