# WhatsApp to MT5 XAUUSD Trading Bot

[![Phase](https://img.shields.io/badge/Phase-5%20of%2012%20Campaign%20Complete-blue)](#current-phase)
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

- **Completed Phases**: **Prompts 1–5 of 12 Completed**
- **Next Phase**: **Prompt 6 — Entry Ladder, TP Allocation and Risk Engine**
- **Implementation Status**: Campaign State Machine, Exact & SHA-256 Semantic Duplicate Protection, Follow-up Command Attachment, Explicit Re-entry, Deterministic Parser, SQLite Persistence, and Shared Domain Contracts implemented. Zero live trading, MT5 execution, or WhatsApp connection code present.

---

## Documentation Registry

- 📋 [REQUIREMENTS.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/REQUIREMENTS.md)
- 🏗️ [ARCHITECTURE.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/ARCHITECTURE.md)
- 📈 [TRADING_RULES.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/TRADING_RULES.md)
- 🔍 [PARSER_ARCHITECTURE.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PARSER_ARCHITECTURE.md)
- 🛡️ [CAMPAIGN_IMPLEMENTATION.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/CAMPAIGN_IMPLEMENTATION.md)
- 🔄 [CAMPAIGN_STATE_MACHINE.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/CAMPAIGN_STATE_MACHINE.md)
- 🔑 [DUPLICATE_PROTECTION.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/DUPLICATE_PROTECTION.md)
- 🎯 [CAMPAIGN_MATCHING.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/CAMPAIGN_MATCHING.md)
- 🔁 [REENTRY.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/REENTRY.md)
- ✅ [CONFIRMATION_WORKFLOW.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/CONFIRMATION_WORKFLOW.md)
- 🌐 [CAMPAIGN_API.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/CAMPAIGN_API.md)
- 📝 [PHASE_5_REPORT.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PHASE_5_REPORT.md)
