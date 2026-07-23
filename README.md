# WhatsApp to MT5 XAUUSD Trading Bot

[![Phase](https://img.shields.io/badge/Phase-8%20of%2012%20WhatsApp%20Worker%20Complete-blue)](#current-phase)
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

- **Completed Phases**: **Prompts 1–8 of 12 Completed**
- **Next Phase**: **Prompt 9 — Full FastAPI Orchestration & Real-Time Events**
- **Implementation Status**: OpenWA WhatsApp Worker (Fake & Real OpenWA Adapters, Single Process Lock, Single Group/Admin Filtering, Durable File Spool, Authenticated Local HTTP Delivery), MT5 Adapter, Single-Writer Execution Queue, Pre-Send Order Check, Order/Position Services, Emergency Close-All, Local Bearer Token API Authentication, Entry Ladder Planning, Risk Engine Validation, Campaign State Machine, Duplicate Protection, Deterministic Parser, SQLite Persistence, and Shared Domain Contracts implemented. Zero live trading, MT5 live account execution, or direct WhatsApp-to-MT5 execution code present.

---

## Documentation Registry

- 📋 [REQUIREMENTS.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/REQUIREMENTS.md)
- 🏗️ [ARCHITECTURE.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/ARCHITECTURE.md)
- 📈 [TRADING_RULES.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/TRADING_RULES.md)
- 📱 [WHATSAPP_WORKER.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/WHATSAPP_WORKER.md)
- 🔒 [WHATSAPP_SECURITY.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/WHATSAPP_SECURITY.md)
- 📁 [WHATSAPP_SPOOL.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/WHATSAPP_SPOOL.md)
- 🌐 [WHATSAPP_API.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/WHATSAPP_API.md)
- 🧪 [WHATSAPP_SMOKE_TESTS.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/WHATSAPP_SMOKE_TESTS.md)
- 🔌 [MT5_ADAPTER.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/MT5_ADAPTER.md)
- 🛡️ [MT5_DEMO_SAFETY.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/MT5_DEMO_SAFETY.md)
- 📑 [PHASE_8_REPORT.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PHASE_8_REPORT.md)
