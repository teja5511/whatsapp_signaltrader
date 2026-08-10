# WhatsApp to MetaTrader 5 (MT5) Gold Trading Bot

A production-oriented, high-reliability Windows desktop application that listens to trading signals in a designated WhatsApp group, parses them deterministically, and places pending order grids (Buy/Sell Limits & Stops) instantly on MetaTrader 5 (restricted to **Exness MT5 Hedging Demo** accounts for safety).

---

> [!CAUTION]
> ### Safety & Demo Account Enforcement
> **This system is hard-coded to reject live trading.** The execution engine strictly validates that the connected MT5 account is a **Demo/Trial account** with **Hedging mode enabled**. If a live account or netting mode is detected, the adapter will immediately block initialization.

---

## ⚡ Key Functions & Capabilities

### 1. Deterministic Signal Parsing
Every incoming WhatsApp message is parsed to extract key trading details.
* **Asset**: Restricted to `XAUUSD` (Gold). All other instruments are ignored.
* **Directions**: `BUY` and `SELL` signals.
* **Order Grids**: Supports entry zones (e.g., `4092-4100`), dividing the lot size across a multi-order ladder grid (start, middle, and end prices).
* **TP/SL Targets**: Parsed automatically (e.g., `tp - 4062`, `tp - 4022`, `sl - 4108`).
* **100 Pips Fallback Policy**: If a Take Profit is marked as `tp - Open`, the bot automatically calculates a 100 pips (10.0 points for Gold) TP target from that specific entry order price.

### 2. Dynamic Order Type Resolution
To avoid MT5 terminal execution errors, the bot automatically determines the correct pending order type at execution time by comparing target entry prices against the live bid/ask tick:
* **BUY Signals**:
  * Price below market $\rightarrow$ **`BUY_LIMIT`**
  * Price above market $\rightarrow$ **`BUY_STOP`**
* **SELL Signals**:
  * Price above market $\rightarrow$ **`SELL_LIMIT`**
  * Price below market $\rightarrow$ **`SELL_STOP`**

### 3. Ultra-Low Latency Execution
Minimizes entry delays through a high-performance database-to-terminal pipeline:
* **Immediate Threaded Dispatch**: Trades are dispatched to MT5 via background threads within **< 150 milliseconds** from the moment the WhatsApp signal is received.
* **Optimized IPC**: Implements caching for `account_info` and removes redundant verification roundtrips to the MT5 terminal to speed up execution.

### 4. Admin & Duplicate Protection Gates
* **Authorized Admin Validator**: Restricts signal parsing exclusively to messages coming from the designated admin JID.
* **Group Validator**: Only monitors the designated WhatsApp group JID.
* **Double-De-duplication**: Filters out repeats using both the unique WhatsApp message ID and semantic fingerprint hashes.

---

## 🏗️ Architecture Overview

The codebase is structured as a monorepo containing three core components:

```
whatsapp-trading-bot/
├── apps/
│   ├── whatsapp-worker/    # Node.js + Baileys service listening to WhatsApp Web
│   ├── trading-service/    # FastAPI Python backend managing orchestration & MT5
│   └── desktop/            # React + Tauri desktop dashboard UI
├── packages/
│   ├── shared-contracts/   # TypeScript/Python shared schemas
│   └── ui/                 # Shared frontend design system
└── .env.example            # Configuration template
```

* **WhatsApp Worker**: A Node.js daemon using Baileys to connect directly with WhatsApp Web (no browser wrapper required). It parses inbound messages and forwards verified signals to the Python server.
* **Trading Service**: A FastAPI Python application running an SQLite database, tracking campaign state machines, managing risk limits, and communicating with the MT5 Windows terminal via the official `MetaTrader5` Python package.
* **Desktop Dashboard**: A React frontend built on Tauri (Rust backend proxy) that displays active campaigns, open positions, connection status, logs, and controls (emergency stop, automation pause/resume).

---

## ⚙️ Setup & Configuration

### Prerequisites
* **OS**: Windows 10/11 (MetaTrader 5 library requirement).
* **Software**: MetaTrader 5 Terminal installed and logged into an **Exness Hedging Demo account**.
* **Runtime**: Node.js (v18+) and Python (v3.10+).

### Step 1: Install Dependencies
From the root directory, install all Node and Python dependencies:
```bash
# Install node packages
pnpm install

# Set up Python virtual environment
cd apps/trading-service
python -m venv .venv
.venv\Scripts\activate
pip install -r pyproject.toml
```

### Step 2: Configure Environment
Copy the configuration template and populate it with your credentials:
```bash
cp .env.example .env
```
Update `.env` with:
* `MT5_LOGIN` and `MT5_PASSWORD` (Your Exness Demo credentials).
* `MT5_SERVER` (e.g., `Exness-MT5Trial6`).
* `APPROVED_GROUP_JID` (Target WhatsApp Group JID).
* `APPROVED_ADMIN_JID` (Sender's WhatsApp Phone Number + suffix, e.g. `123456789@s.whatsapp.net`).

---

## 🚀 Running the Bot

### 1. Start the WhatsApp Worker
Connect the worker to WhatsApp Web. On first launch, a QR code will print in the console—scan it with your WhatsApp mobile app:
```bash
pnpm whatsapp:dev
```

### 2. Start the Python Backend
Navigate into the trading service directory and launch the FastAPI web server:

**Step-by-step (PowerShell / Windows Terminal):**
```powershell
cd apps/trading-service
.\.venv\Scripts\activate
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

**Single-line Copy & Paste (PowerShell):**
```powershell
cd apps/trading-service; $env:MT5_ADAPTER_MODE="real"; python -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

### 3. Launch the Desktop Dashboard
Run the Tauri app to open the visual UI console:
```bash
pnpm desktop:dev
```
