import React, { useState } from "react";
import { useUiStore } from "../stores/uiStore";
import { Button } from "./ui/Button";
import { AlertTriangle, Lock } from "lucide-react";

export const ConfirmDialog: React.FC = () => {
  const { activeConfirmModal, closeConfirmModal } = useUiStore();
  const [typedPhrase, setTypedPhrase] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!activeConfirmModal.type) return null;

  const { title, description, phrase, action } = activeConfirmModal;

  const isMatched = typedPhrase.trim() === phrase;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isMatched || !action) return;

    setLoading(true);
    setError(null);
    try {
      await action();
      closeConfirmModal();
      setTypedPhrase("");
    } catch (err: any) {
      setError(err.message || "Action failed to execute.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700/80 rounded-xl max-w-lg w-full p-6 shadow-2xl space-y-5 font-mono">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-lg bg-rose-950/80 border border-rose-700/50 flex items-center justify-center shrink-0">
            <AlertTriangle className="w-6 h-6 text-rose-400" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100">{title || "Confirm Dangerous Operation"}</h2>
            <p className="text-xs text-slate-300 mt-1 leading-relaxed">{description}</p>
          </div>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-rose-950/90 border border-rose-700/80 text-rose-200 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1">
              Type exact phrase to confirm: <span className="text-sky-400 font-bold select-all">{phrase}</span>
            </label>
            <input
              type="text"
              value={typedPhrase}
              onChange={(e) => setTypedPhrase(e.target.value)}
              placeholder={phrase}
              className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-700 rounded-lg text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-rose-500 font-mono tracking-wide"
              autoFocus
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <Button type="button" variant="secondary" onClick={() => { closeConfirmModal(); setTypedPhrase(""); }}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="danger"
              disabled={!isMatched || loading}
            >
              {loading ? "Executing..." : "Confirm & Execute"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
