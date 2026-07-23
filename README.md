# WhatsApp to MT5 XAUUSD Trading Bot

[![Phase](https://img.shields.io/badge/Phase-7%20of%2012%20MT5%20Adapter%20Complete-blue)](#current-phase)
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

- **Completed Phases**: **Prompts 1–7 of 12 Completed**
- **Next Phase**: **Prompt 8 — OpenWA WhatsApp Worker**
- **Implementation Status**: MT5 Adapter (Fake, Dry Run, Real Demo), Single-Writer Execution Queue, Pre-Send Order Check, Order/Position Services, Emergency Close-All, Local Bearer Token API Authentication, Entry Ladder Planning, Risk Engine Validation, Campaign State Machine, Duplicate Protection, Deterministic Parser, SQLite Persistence, and Shared Domain Contracts implemented. Zero live trading, MT5 live account execution, or WhatsApp connection code present.

---

## Documentation Registry

- 📋 [REQUIREMENTS.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/REQUIREMENTS.md)
- 🏗️ [ARCHITECTURE.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/ARCHITECTURE.md)
- 📈 [TRADING_RULES.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/TRADING_RULES.md)
- 🔌 [MT5_ADAPTER.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/MT5_ADAPTER.md)
- 🛡️ [MT5_DEMO_SAFETY.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/MT5_DEMO_SAFETY.md)
- 🔍 [MT5_SYMBOL_RESOLUTION.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/MT5_SYMBOL_RESOLUTION.md)
- ⚙️ [MT5_EXECUTION_WORKER.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/MT5_EXECUTION_WORKER.md)
- 📝 [MT5_ORDER_LIFECYCLE.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/MT5_ORDER_LIFECYCLE.md)
- 📊 [MT5_POSITION_OPERATIONS.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/MT5_POSITION_OPERATIONS.md)
- 🌐 [MT5_API.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/MT5_API.md)
- 🧪 [MT5_SMOKE_TESTS.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/MT5_SMOKE_TESTS.md)
- 📑 [PHASE_7_REPORT.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PHASE_7_REPORT.md)
