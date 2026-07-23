# WhatsApp to MT5 XAUUSD Trading Bot

[![Phase](https://img.shields.io/badge/Phase-4%20of%2012%20Parser%20Complete-blue)](#current-phase)
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

- **Completed Phases**: **Prompts 1–4 of 12 Completed**
- **Next Phase**: **Prompt 5 — Campaign State Machine and Duplicate Protection**
- **Implementation Status**: Deterministic Signal & Command Parser, SQLite Persistence, Database Models, and Shared Domain Contracts implemented. Zero live trading, MT5 execution, or WhatsApp connection code present.

---

## Documentation Registry

- 📋 [REQUIREMENTS.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/REQUIREMENTS.md)
- 🏗️ [ARCHITECTURE.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/ARCHITECTURE.md)
- 📈 [TRADING_RULES.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/TRADING_RULES.md)
- 🔍 [PARSER_ARCHITECTURE.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PARSER_ARCHITECTURE.md)
- ⚡ [PARSER_RULES.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PARSER_RULES.md)
- 📊 [PARSER_CLASSIFICATION.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PARSER_CLASSIFICATION.md)
- 🧪 [PARSER_FIXTURES.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PARSER_FIXTURES.md)
- 🌐 [PARSER_API.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PARSER_API.md)
- 🏷️ [PARSER_VERSIONING.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PARSER_VERSIONING.md)
- 📝 [PHASE_4_REPORT.md](file:///c:/Users/Pavan%20Teja/projects/whatsapp_trading%20bot/docs/PHASE_4_REPORT.md)
