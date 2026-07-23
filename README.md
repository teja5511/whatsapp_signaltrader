# WhatsApp to MT5 XAUUSD Trading Bot

[![Phase](https://img.shields.io/badge/Phase-6%20of%2012%20Planning%20Complete-blue)](#current-phase)
[![Target OS](https://img.shields.io/badge/OS-Windows%2010%2F11-0078D6)](#architecture-summary)
[![Instrument](https://img.shields.io/badge/Instrument-XAUUSD-FFD700)](#confirmed-restrictions)

A production-oriented, high-reliability Windows desktop application that converts approved WhatsApp group trading signals into MetaTrader 5 (MT5) pending order grids and manages position lifecycles on an Exness hedging account.

---

> [!CAUTION]
> ### Safety & Risk Notice
> **DO NOT RUN THIS APPLICATION AGAINST A LIVE TRADING ACCOUNT.**  
> This software is strictly intended for operation on an **Exness MT5 Demo Account**. Trading spot gold (XAUUSD) carries substantial financial risk. The developers assume no responsibility for financial losses incurred through the use of this software.

---

## Current Status

- **Completed Phases**: **Prompts 1–6 of 12 Completed**
- **Next Phase**: **Prompt 7 — MT5 Adapter and Demo Execution Worker**
- **Implementation Status**: Entry Ladder Calculations, TP Allocation (100-pip, TP1, TP2), Risk Engine Validation, SHA-256 Planning Fingerprinting, Campaign State Machine, Duplicate Protection, Deterministic Parser, SQLite Persistence, and Shared Domain Contracts implemented. Zero live trading, MT5 execution, or WhatsApp connection code present.

---

## Documentation Registry

- 📋 [REQUIREMENTS.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/REQUIREMENTS.md)
- 🏗️ [ARCHITECTURE.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/ARCHITECTURE.md)
- 📈 [TRADING_RULES.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/TRADING_RULES.md)
- 📐 [ENTRY_PLANNER.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/ENTRY_PLANNER.md)
- 🪜 [ENTRY_LADDER.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/ENTRY_LADDER.md)
- 🎯 [TP_ALLOCATION.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/TP_ALLOCATION.md)
- 🛡️ [RISK_ENGINE.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/RISK_ENGINE.md)
- 📜 [PLANNING_POLICIES.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PLANNING_POLICIES.md)
- 📊 [SYMBOL_SPECIFICATION.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/SYMBOL_SPECIFICATION.md)
- 🌐 [PLANNING_API.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PLANNING_API.md)
- 📝 [PHASE_6_REPORT.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PHASE_6_REPORT.md)
