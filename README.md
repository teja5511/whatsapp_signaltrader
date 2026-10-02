# WhatsApp Signal Trader

A Windows app that reads gold signals from a WhatsApp group you choose and places the matching pending orders on a MetaTrader 5 demo account.

One command starts the trading service, the WhatsApp worker, and the dashboard.

## Safety

Orders are sent only to a **demo hedging** account. A live account or a netting account is rejected before any order is placed.

MetaTrader must be open, logged in, and **Algo Trading** must be on. If the toolbar button is off, the terminal returns `AutoTrading disabled by client` and nothing is placed.

## How a signal is traded

Gold only (`XAUUSD`). Other instruments are ignored.

```
Gold Sell
4120-4128
sl - 4136
tp - 4112
tp - 4104
tp - Open
```

- The zone includes both ends. `4120-4128` with the default 5 entries becomes 4120, 4122, 4124, 4126, 4128. Entry count can be 3 to 8.
- The lot size applies to **each** entry. Five entries at 0.30 is 1.50 lots total. If the total would exceed 2.00 lots, the signal is blocked. Lots are never shrunk to fit.
- The first entry uses the signal's first numeric target. The second entry uses the second numeric target. Every other entry uses a 100-pip target, which on gold is a price move of 10.00. A sell at 4128 targets 4118. A buy at 4120 targets 4130.
- `tp - Open` is stored with the signal. It does not leave an order without a target.
- If a numeric target is missing, that slot uses the same 10.00 distance and the orders are still placed.
- The order type is chosen from the live quote when the order is sent:
  - Buy below the market is `BUY_LIMIT`. Buy above the market is `BUY_STOP`.
  - Sell above the market is `SELL_LIMIT`. Sell below the market is `SELL_STOP`.
- If price is already inside the zone, or has moved past it, the full ladder is still placed. Each level is a limit or a stop from the live quote.
- A new signal can run beside an existing one. Filled positions stay open.
- `Secure profits`, `Exit on your comfort`, and `Hold it` are commands. They are not new entry signals.

## Requirements

- Windows 10 or 11
- MetaTrader 5, logged into a demo hedging account
- Node.js 18 or newer, and [pnpm](https://pnpm.io/)
- Python 3.11 or newer

## Setup

From the project folder:

```powershell
pnpm install
python -m pip install -e ".[dev]"
python -m pip install MetaTrader5 python-dotenv
copy .env.example .env
```

Fill in `.env`. Do not commit that file.

| Variable | Purpose |
| --- | --- |
| `MT5_LOGIN` | Demo account login |
| `MT5_PASSWORD` | Demo account password |
| `MT5_SERVER` | Server name shown in MetaTrader, such as `MetaQuotes-Demo` |
| `MT5_ADAPTER_MODE` | `real` to send orders to the terminal |
| `APPROVED_GROUP_JID` | Fallback group, used only when no group has been saved in the dashboard |
| `LOCAL_API_TOKEN` | Shared secret between the dashboard and the local services |

Groups you enable on the WhatsApp page are the groups that are traded. Messages you send yourself in an enabled group are accepted, so you can test from the linked account. `APPROVED_ADMIN_JID` applies only when no group has been added.

## Run

Open MetaTrader and turn Algo Trading on, then from the project folder:

```powershell
pnpm start
```

That starts:

| Service | Address |
| --- | --- |
| Trading service | http://127.0.0.1:8000 |
| WhatsApp worker | http://127.0.0.1:8010 |
| Dashboard | http://localhost:1420 |

The dashboard opens in the browser. On the **WhatsApp** page, scan the QR code from the phone: WhatsApp, Linked devices, Link a device. Add the signal group on that same page and leave it enabled.

Pending orders, open positions, and the execution queue are on the **Positions** page.

## Layout

```
apps/whatsapp-worker/   Baileys client. Reads the group and forwards messages.
apps/trading-service/   FastAPI service. Parses the signal, plans the ladder, sends MT5 orders.
apps/desktop/           Dashboard at http://localhost:1420
packages/               Shared contracts and UI pieces
docs/TRADING_RULES.md   Entry, lot, and target rules
scripts/run-all.ps1     The command behind pnpm start
```

## What stays off GitHub

`.env`, the WhatsApp session under `apps/whatsapp-worker/data/`, and the SQLite database `apps/trading-service/trading_bot.db` are local. They are listed in `.gitignore`.
