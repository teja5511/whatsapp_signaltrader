import React, { useEffect, useState } from 'react';
import { DESIGN_TOKENS } from '@whatsapp-bot/ui';

export default function App() {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/status')
      .then((res) => res.json())
      .then((data) => setStatus(data))
      .catch(() => setStatus(null));
  }, []);

  return (
    <div style={{ padding: '2rem', backgroundColor: DESIGN_TOKENS.colors.backgroundDark, minHeight: '100vh' }}>
      <header style={{ borderBottom: '1px solid #334155', paddingBottom: '1rem', marginBottom: '2rem' }}>
        <h1 style={{ margin: 0, color: DESIGN_TOKENS.colors.primary }}>WhatsApp MT5 XAUUSD Bot</h1>
        <p style={{ margin: '0.5rem 0 0 0', color: '#94a3b8' }}>Desktop Dashboard Shell — Phase 2 Scaffolding</p>
      </header>

      <main>
        <div style={{ backgroundColor: DESIGN_TOKENS.colors.cardDark, padding: '1.5rem', borderRadius: '8px', border: '1px solid #334155' }}>
          <h2>System Status</h2>
          {status ? (
            <div>
              <p><strong>Instrument:</strong> {status.instrument}</p>
              <p><strong>Account Mode:</strong> <span style={{ color: DESIGN_TOKENS.colors.success }}>{status.account_mode}</span></p>
              <p><strong>Execution Mode:</strong> {status.execution_mode}</p>
              <p><strong>Default Entries:</strong> {status.default_entry_count}</p>
              <p><strong>Max Exposure Cap:</strong> {status.max_exposure_lots} lots</p>
            </div>
          ) : (
            <p style={{ color: DESIGN_TOKENS.colors.warning }}>Connecting to Python Trading Core (http://localhost:8000)...</p>
          )}
        </div>
      </main>
    </div>
  );
}
