# Parser Test Fixtures Documentation

Document Version: 1.0.0 (Phase 4 Parser)  
Status: Approved & Implemented  

---

## Fixture Registry Location
Test fixtures are stored in `packages/parser-fixtures/fixtures/`:

- `new-signals/`: Benchmark trade signals (`gold_sell.json`, `gold_buy_limit.json`).
- `ambiguous/`: Ambiguous phrases requiring user confirmation (`secure_profits.json`).
- `unsupported/`: Unsupported instrument tests (`btc_signal.json`).

## Adding Regression Cases
To add a new fixture:
1. Create a JSON file in the appropriate category directory in `packages/parser-fixtures/fixtures/`.
2. Structure the payload with `name`, `source`, `input` (containing `text`), and `expected` classification attributes.
3. Register the export in `packages/parser-fixtures/src/index.ts`.
