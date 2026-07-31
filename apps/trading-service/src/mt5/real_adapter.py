"""Real MetaTrader 5 Python Package Adapter with Strict Demo-Only Safety Gates."""

import os
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone

from src.mt5.constants import (
    MODE_REAL, HEALTH_NOT_INITIALIZED, HEALTH_READY, HEALTH_NOT_INSTALLED,
    HEALTH_BLOCKED_LIVE_ACCOUNT, HEALTH_BLOCKED_NON_HEDGING, HEALTH_BLOCKED_ACCOUNT_NOT_ALLOWED,
    HEALTH_BLOCKED_SERVER_NOT_ALLOWED, HEALTH_BLOCKED_SYMBOL_NOT_FOUND, HEALTH_BLOCKED_SYMBOL_AMBIGUOUS,
    HEALTH_TRADING_NOT_ALLOWED, HEALTH_ERROR, ENV_DEMO, ENV_REAL, ENV_CONTEST, ENV_UNKNOWN,
    MARGIN_HEDGING, MARGIN_NETTING, MARGIN_EXCHANGE, MARGIN_UNKNOWN, CANONICAL_SYMBOL_XAUUSD,
    FILLING_FOK, FILLING_IOC, FILLING_RETURN, TIME_GTC
)
from src.mt5.contracts import (
    Mt5TerminalInfoDTO, Mt5AccountInfoDTO, Mt5SymbolResolutionDTO,
    Mt5SymbolSpecificationDTO, Mt5OrderCheckRequestDTO, Mt5OrderCheckResultDTO,
    Mt5OrderSendRequestDTO, Mt5OrderSendResultDTO, Mt5OrderSnapshotDTO,
    Mt5PositionSnapshotDTO, Mt5StatusDTO, Mt5TickDTO, Mt5HistoryOrderDTO,
    Mt5MutationResultDTO
)
from src.mt5.adapter import MT5AdapterInterface
from src.mt5.errors import (
    MT5PackageUnavailableError, MT5InitializeFailedError, MT5LiveAccountBlockedError,
    MT5AccountNotHedgingError, MT5AccountNotAllowedError, MT5ServerNotAllowedError,
    XAUUSDSymbolNotFoundError, XAUUSDSymbolAmbiguousError, OrderCheckFailedError
)

try:
    import MetaTrader5 as mt5
    HAS_MT5_PACKAGE = True
except ImportError:
    mt5 = None
    HAS_MT5_PACKAGE = False

class RealMT5Adapter(MT5AdapterInterface):
    def __init__(
        self,
        terminal_path: Optional[str] = None,
        allowed_logins: Optional[List[int]] = None,
        allowed_servers: Optional[List[str]] = None,
        symbol_override: Optional[str] = None
    ):
        self._terminal_path = terminal_path or os.getenv("MT5_TERMINAL_PATH")
        self._allowed_logins = allowed_logins
        self._allowed_servers = allowed_servers
        self._symbol_override = symbol_override or os.getenv("MT5_SYMBOL_OVERRIDE")
        self._initialized = False
        self._health_state = HEALTH_NOT_INITIALIZED

    @property
    def mode(self) -> str:
        return MODE_REAL

    @property
    def health_state(self) -> str:
        return self._health_state

    def initialize(self) -> bool:
        if not HAS_MT5_PACKAGE:
            self._health_state = HEALTH_NOT_INSTALLED
            raise MT5PackageUnavailableError("MetaTrader5 python module is not installed.")

        # Initialize MT5 terminal connection with credentials if available
        init_kwargs = {}
        if self._terminal_path and os.path.exists(self._terminal_path):
            init_kwargs["path"] = self._terminal_path

        env_login = os.getenv("MT5_LOGIN")
        env_password = os.getenv("MT5_PASSWORD")
        env_server = os.getenv("MT5_SERVER")
        if env_login and env_login.strip().isdigit():
            init_kwargs["login"] = int(env_login.strip())
        if env_password:
            init_kwargs["password"] = env_password
        if env_server:
            init_kwargs["server"] = env_server

        ok = mt5.initialize(**init_kwargs)
        if not ok:
            err = mt5.last_error()
            self._health_state = HEALTH_ERROR
            raise MT5InitializeFailedError(f"MT5 initialize returned False. Last error: {err}")

        # Verify Account & Safety Gates
        acc_dto = self.account_info()

        # Gate 1: Must be DEMO environment
        if acc_dto.environment_kind != ENV_DEMO:
            self._health_state = HEALTH_BLOCKED_LIVE_ACCOUNT
            self.shutdown()
            raise MT5LiveAccountBlockedError(acc_dto.login, acc_dto.environment_kind)

        # Gate 2: Must be HEDGING margin mode
        if acc_dto.margin_mode != MARGIN_HEDGING:
            self._health_state = HEALTH_BLOCKED_NON_HEDGING
            self.shutdown()
            raise MT5AccountNotHedgingError(acc_dto.margin_mode)

        # Gate 3: Allowed logins check
        if self._allowed_logins and acc_dto.login not in self._allowed_logins:
            self._health_state = HEALTH_BLOCKED_ACCOUNT_NOT_ALLOWED
            self.shutdown()
            raise MT5AccountNotAllowedError(acc_dto.login)

        # Gate 4: Allowed servers check
        if self._allowed_servers and acc_dto.server not in self._allowed_servers:
            self._health_state = HEALTH_BLOCKED_SERVER_NOT_ALLOWED
            self.shutdown()
            raise MT5ServerNotAllowedError(acc_dto.server)

        # Gate 5: Terminal & Account trade permission
        term_dto = self.terminal_info()
        if not term_dto.trade_allowed or not acc_dto.trade_allowed:
            self._health_state = HEALTH_TRADING_NOT_ALLOWED
            self.shutdown()
            return False

        # Gate 6: Resolve XAUUSD symbol
        resolution = self.resolve_symbol()
        if not resolution.is_resolved:
            if resolution.source == "AMBIGUOUS":
                self._health_state = HEALTH_BLOCKED_SYMBOL_AMBIGUOUS
                self.shutdown()
                raise XAUUSDSymbolAmbiguousError(["XAUUSD", "XAUUSDm"])
            else:
                self._health_state = HEALTH_BLOCKED_SYMBOL_NOT_FOUND
                self.shutdown()
                raise XAUUSDSymbolNotFoundError("No tradable XAUUSD symbol resolved.")

        self._initialized = True
        self._health_state = HEALTH_READY
        return True

    def shutdown(self) -> None:
        if HAS_MT5_PACKAGE:
            try:
                mt5.shutdown()
            except Exception:
                pass
        self._initialized = False
        self._health_state = HEALTH_NOT_INITIALIZED

    def is_initialized(self) -> bool:
        return self._initialized and self._health_state == HEALTH_READY

    def terminal_info(self) -> Mt5TerminalInfoDTO:
        if not HAS_MT5_PACKAGE:
            return Mt5TerminalInfoDTO(connected=False, trade_allowed=False)
        info = mt5.terminal_info()
        if info is None:
            return Mt5TerminalInfoDTO(connected=False, trade_allowed=False)
        return Mt5TerminalInfoDTO(
            connected=bool(info.connected),
            trade_allowed=bool(info.trade_allowed),
            name=str(info.name or "MetaTrader 5"),
            path=str(info.path or ""),
            company=str(info.company or "")
        )

    def account_info(self) -> Mt5AccountInfoDTO:
        if not HAS_MT5_PACKAGE:
            raise MT5PackageUnavailableError()
        info = mt5.account_info()
        if info is None:
            raise MT5InitializeFailedError("mt5.account_info() returned None.")

        # Detect Demo vs Real
        # In MT5: trade_mode: 0 = ACCOUNT_TRADE_MODE_DEMO, 1 = CONTEST, 2 = REAL
        trade_mode = getattr(info, "trade_mode", None)
        server_name = (getattr(info, "server", "") or "").lower()

        if trade_mode == 0 or "demo" in server_name or "trial" in server_name:
            env_kind = ENV_DEMO
        elif trade_mode == 1:
            env_kind = ENV_CONTEST
        elif trade_mode == 2 or "real" in server_name:
            env_kind = ENV_REAL
        else:
            env_kind = ENV_UNKNOWN

        # Margin mode: 0 = ACCOUNT_MARGIN_MODE_NETTING, 1 = EXCHANGE, 2 = HEDGING
        margin_mode_raw = getattr(info, "margin_mode", None)
        if margin_mode_raw == 2:
            margin_mode = MARGIN_HEDGING
        elif margin_mode_raw == 0:
            margin_mode = MARGIN_NETTING
        elif margin_mode_raw == 1:
            margin_mode = MARGIN_EXCHANGE
        else:
            margin_mode = MARGIN_UNKNOWN

        login_val = int(info.login)
        login_str = str(login_val)
        masked = f"{login_str[:4]}****" if len(login_str) >= 4 else "****"

        return Mt5AccountInfoDTO(
            login=login_val,
            login_masked=masked,
            server=str(info.server or ""),
            company=str(info.company or ""),
            environment_kind=env_kind,
            margin_mode=margin_mode,
            currency=str(info.currency or "USD"),
            leverage=int(info.leverage or 100),
            balance=Decimal(str(info.balance)),
            equity=Decimal(str(info.equity)),
            margin=Decimal(str(info.margin)),
            margin_free=Decimal(str(info.margin_free)),
            trade_allowed=bool(info.trade_allowed),
            trade_expert=bool(info.trade_expert)
        )

    def list_symbols(self) -> List[str]:
        if not HAS_MT5_PACKAGE:
            return []
        syms = mt5.symbols_get()
        if not syms:
            return []
        return [s.name for s in syms]

    def resolve_symbol(self, canonical: str = "XAUUSD") -> Mt5SymbolResolutionDTO:
        if self._symbol_override:
            return Mt5SymbolResolutionDTO(canonical_symbol=canonical, broker_symbol=self._symbol_override, is_resolved=True, source="OVERRIDE")

        available = self.list_symbols()
        if canonical in available:
            return Mt5SymbolResolutionDTO(canonical_symbol=canonical, broker_symbol=canonical, is_resolved=True, source="EXACT_MATCH")

        # Check suffix variants starting with XAUUSD
        matches = [s for s in available if s.upper().startswith("XAUUSD")]
        if len(matches) == 1:
            return Mt5SymbolResolutionDTO(canonical_symbol=canonical, broker_symbol=matches[0], is_resolved=True, source="SUFFIX_VARIANT")
        elif len(matches) > 1:
            return Mt5SymbolResolutionDTO(canonical_symbol=canonical, broker_symbol="", is_resolved=False, source="AMBIGUOUS")

        if "GOLD" in available:
            return Mt5SymbolResolutionDTO(canonical_symbol=canonical, broker_symbol="GOLD", is_resolved=True, source="GOLD_ALIAS")

        return Mt5SymbolResolutionDTO(canonical_symbol=canonical, broker_symbol="", is_resolved=False, source="NOT_FOUND")

    def symbol_specification(self, symbol: str = "XAUUSD") -> Mt5SymbolSpecificationDTO:
        if not HAS_MT5_PACKAGE:
            raise MT5PackageUnavailableError()

        broker_symbol = symbol
        if symbol == "XAUUSD":
            res = self.resolve_symbol("XAUUSD")
            if res.is_resolved:
                broker_symbol = res.broker_symbol

        mt5.symbol_select(broker_symbol, True)
        info = mt5.symbol_info(broker_symbol)
        if info is None:
            raise XAUUSDSymbolNotFoundError(f"Symbol '{broker_symbol}' not found on broker.")

        # Determine filling mode
        filling_mode = FILLING_RETURN
        if hasattr(info, "filling_mode"):
            fm = info.filling_mode
            if fm & 1:  # FOK
                filling_mode = FILLING_FOK
            elif fm & 2:  # IOC
                filling_mode = FILLING_IOC

        return Mt5SymbolSpecificationDTO(
            symbol=info.name,
            digits=int(info.digits),
            point=Decimal(str(info.point)),
            tick_size=Decimal(str(getattr(info, "trade_tick_size", info.point))),
            volume_min=Decimal(str(info.volume_min)),
            volume_max=Decimal(str(info.volume_max)),
            volume_step=Decimal(str(info.volume_step)),
            stops_level_points=int(getattr(info, "trade_stops_level", 0)),
            freeze_level_points=int(getattr(info, "trade_freeze_level", 0)),
            trade_mode="FULL" if getattr(info, "trade_mode", 4) == 4 else str(info.trade_mode),
            contract_size=Decimal(str(getattr(info, "trade_contract_size", 100.0))),
            filling_mode=filling_mode,
            source="BROKER_MT5"
        )

    def order_check(self, req: Mt5OrderCheckRequestDTO) -> Mt5OrderCheckResultDTO:
        if not HAS_MT5_PACKAGE or not self._initialized:
            raise MT5InitializeFailedError("Adapter not initialized for order_check.")

        order_type_val = mt5.ORDER_TYPE_BUY_LIMIT if req.order_type == "BUY_LIMIT" else mt5.ORDER_TYPE_SELL_LIMIT
        type_filling = mt5.ORDER_FILLING_RETURN
        if req.filling_type == FILLING_FOK:
            type_filling = mt5.ORDER_FILLING_FOK
        elif req.filling_type == FILLING_IOC:
            type_filling = mt5.ORDER_FILLING_IOC

        request_dict = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": req.symbol,
            "volume": float(req.volume),
            "type": order_type_val,
            "price": float(req.price),
            "sl": float(req.stop_loss),
            "tp": float(req.take_profit) if req.take_profit is not None else 0.0,
            "magic": req.magic_number,
            "comment": req.comment,
            "type_filling": type_filling,
            "type_time": mt5.ORDER_TIME_GTC
        }

        res = mt5.order_check(request_dict)
        if res is None:
            err = mt5.last_error()
            return Mt5OrderCheckResultDTO(retcode=err[0], retcode_name="CHECK_FAILED", is_valid=False, comment=str(err[1]))

        return Mt5OrderCheckResultDTO(
            retcode=int(res.retcode),
            retcode_name=str(getattr(res, "comment", "OK")),
            is_valid=int(res.retcode) == 0,
            comment=str(getattr(res, "comment", "OK")),
            margin=Decimal(str(getattr(res, "margin", 0.0))),
            margin_free=Decimal(str(getattr(res, "margin_free", 0.0)))
        )

    def order_send(self, req: Mt5OrderSendRequestDTO) -> Mt5OrderSendResultDTO:
        if not HAS_MT5_PACKAGE or not self.is_initialized():
            raise MT5InitializeFailedError("Adapter not initialized for order_send.")

        # STRICT DEMO SAFETY GATE CHECK BEFORE EVERY SEND
        acc = self.account_info()
        if acc.environment_kind != ENV_DEMO or acc.margin_mode != MARGIN_HEDGING:
            raise MT5LiveAccountBlockedError(acc.login, acc.environment_kind)

        # MANDATORY order_check BEFORE order_send
        check_req = Mt5OrderCheckRequestDTO(
            symbol=req.symbol,
            volume=req.volume,
            order_type=req.order_type,
            price=req.price,
            stop_loss=req.stop_loss,
            take_profit=req.take_profit,
            magic_number=req.magic_number,
            comment=req.comment,
            filling_type=req.filling_type,
            time_type=req.time_type
        )
        check_res = self.order_check(check_req)
        if not check_res.is_valid:
            raise OrderCheckFailedError(check_res.retcode, check_res.retcode_name, check_res.comment)

        # Build raw MT5 order_send request
        order_type_val = mt5.ORDER_TYPE_BUY_LIMIT if req.order_type == "BUY_LIMIT" else mt5.ORDER_TYPE_SELL_LIMIT
        type_filling = mt5.ORDER_FILLING_RETURN
        if req.filling_type == FILLING_FOK:
            type_filling = mt5.ORDER_FILLING_FOK
        elif req.filling_type == FILLING_IOC:
            type_filling = mt5.ORDER_FILLING_IOC

        request_dict = {
            "action": mt5.TRADE_ACTION_PENDING,
            "symbol": req.symbol,
            "volume": float(req.volume),
            "type": order_type_val,
            "price": float(req.price),
            "sl": float(req.stop_loss),
            "tp": float(req.take_profit) if req.take_profit is not None else 0.0,
            "magic": req.magic_number,
            "comment": req.comment,
            "type_filling": type_filling,
            "type_time": mt5.ORDER_TIME_GTC
        }

        res = mt5.order_send(request_dict)
        if res is None:
            err = mt5.last_error()
            return Mt5OrderSendResultDTO(retcode=err[0], retcode_name="SEND_FAILED", volume=req.volume, price=req.price, comment=str(err[1]), is_success=False)

        is_ok = (int(res.retcode) in (10009, 10008))
        return Mt5OrderSendResultDTO(
            retcode=int(res.retcode),
            retcode_name=str(getattr(res, "comment", "")),
            order_ticket=int(res.order) if getattr(res, "order", None) else None,
            deal_ticket=int(res.deal) if getattr(res, "deal", None) else None,
            volume=Decimal(str(getattr(res, "volume", req.volume))),
            price=Decimal(str(getattr(res, "price", req.price))),
            comment=str(getattr(res, "comment", "")),
            is_success=is_ok,
            dry_run=False,
            execution_performed=True
        )

    def orders_get(self, magic_number: Optional[int] = None, ticket: Optional[int] = None) -> List[Mt5OrderSnapshotDTO]:
        if not HAS_MT5_PACKAGE:
            return []
        if not self._initialized:
            try:
                mt5.initialize()
            except Exception:
                pass
        orders = mt5.orders_get()
        if orders is None:
            return []
        res = []
        for o in orders:
            if magic_number is not None and getattr(o, "magic", None) != magic_number:
                continue
            if ticket is not None and getattr(o, "ticket", None) != ticket:
                continue
            o_type = "BUY_LIMIT" if o.type == mt5.ORDER_TYPE_BUY_LIMIT else "SELL_LIMIT"
            res.append(Mt5OrderSnapshotDTO(
                ticket=int(o.ticket),
                magic_number=int(o.magic),
                symbol=str(o.symbol),
                order_type=o_type,
                volume=Decimal(str(o.volume_initial)),
                price=Decimal(str(o.price_open)),
                stop_loss=Decimal(str(o.sl)),
                take_profit=Decimal(str(o.tp)) if o.tp else None,
                comment=str(o.comment or ""),
                state="PLACED"
            ))
        return res

    def positions_get(self, magic_number: Optional[int] = None, ticket: Optional[int] = None) -> List[Mt5PositionSnapshotDTO]:
        if not HAS_MT5_PACKAGE:
            return []
        if not self._initialized:
            try:
                mt5.initialize()
            except Exception:
                pass
        positions = mt5.positions_get()
        if positions is None:
            return []
        res = []
        for p in positions:
            if magic_number is not None and getattr(p, "magic", None) != magic_number:
                continue
            if ticket is not None and getattr(p, "ticket", None) != ticket:
                continue
            p_type = "BUY" if p.type == mt5.POSITION_TYPE_BUY else "SELL"
            res.append(Mt5PositionSnapshotDTO(
                ticket=int(p.ticket),
                magic_number=int(p.magic),
                symbol=str(p.symbol),
                position_type=p_type,
                volume=Decimal(str(p.volume)),
                price_open=Decimal(str(p.price_open)),
                stop_loss=Decimal(str(p.sl)),
                take_profit=Decimal(str(p.tp)) if p.tp else None,
                profit=Decimal(str(p.profit)),
                comment=str(p.comment or ""),
                state="OPEN"
            ))
        return res

    # -- Mutations ----------------------------------------------------------

    def _assert_demo_hedging(self) -> None:
        """Re-verify the account immediately before every mutating call."""
        acc = self.account_info()
        if acc.environment_kind != ENV_DEMO or acc.margin_mode != MARGIN_HEDGING:
            raise MT5LiveAccountBlockedError(acc.login, acc.environment_kind)

    def _send_and_classify(self, request_dict: Dict[str, Any], ticket: int, operation: str) -> Mt5MutationResultDTO:
        """Submit a mutation and classify the outcome.

        A ``None`` result from ``order_send`` means the request may or may not
        have reached the server, so it is reported as ``outcome_unknown`` and
        must be reconciled rather than retried.
        """
        try:
            res = mt5.order_send(request_dict)
        except Exception as exc:  # pragma: no cover - depends on terminal state
            return Mt5MutationResultDTO(
                ticket=ticket, operation=operation, retcode=-1,
                retcode_name="SEND_EXCEPTION", is_success=False,
                outcome_unknown=True, comment=str(exc)
            )

        if res is None:
            err = mt5.last_error()
            return Mt5MutationResultDTO(
                ticket=ticket, operation=operation, retcode=int(err[0]),
                retcode_name="SEND_FAILED", is_success=False,
                outcome_unknown=True, comment=str(err[1])
            )

        retcode = int(res.retcode)
        return Mt5MutationResultDTO(
            ticket=ticket,
            operation=operation,
            retcode=retcode,
            retcode_name=str(getattr(res, "comment", "")) or "TRADE_RETCODE",
            is_success=retcode in (10008, 10009),
            outcome_unknown=False,
            comment=str(getattr(res, "comment", "")),
            closed_volume=Decimal(str(getattr(res, "volume", 0) or 0)) or None,
        )

    def modify_order(
        self,
        ticket: int,
        price: Optional[Decimal] = None,
        sl: Optional[Decimal] = None,
        tp: Optional[Decimal] = None
    ) -> Mt5MutationResultDTO:
        if not HAS_MT5_PACKAGE or not self.is_initialized():
            raise MT5InitializeFailedError("Adapter not initialized for modify_order.")
        self._assert_demo_hedging()

        existing = self.orders_get(ticket=ticket)
        if not existing:
            return Mt5MutationResultDTO(
                ticket=ticket, operation="MODIFY_ORDER", retcode=10013,
                retcode_name="TRADE_RETCODE_INVALID", is_success=False,
                comment=f"Pending order {ticket} not present at broker."
            )
        current = existing[0]

        request_dict = {
            "action": mt5.TRADE_ACTION_MODIFY,
            "order": int(ticket),
            "price": float(price if price is not None else current.price),
            "sl": float(sl if sl is not None else current.stop_loss),
            "tp": float(tp if tp is not None else (current.take_profit or 0)),
            "type_time": mt5.ORDER_TIME_GTC,
        }
        return self._send_and_classify(request_dict, ticket, "MODIFY_ORDER")

    def delete_order(self, ticket: int) -> Mt5MutationResultDTO:
        if not HAS_MT5_PACKAGE or not self.is_initialized():
            raise MT5InitializeFailedError("Adapter not initialized for delete_order.")
        self._assert_demo_hedging()

        request_dict = {"action": mt5.TRADE_ACTION_REMOVE, "order": int(ticket)}
        return self._send_and_classify(request_dict, ticket, "DELETE_ORDER")

    def modify_position(
        self,
        ticket: int,
        sl: Decimal,
        tp: Optional[Decimal] = None
    ) -> Mt5MutationResultDTO:
        if not HAS_MT5_PACKAGE or not self.is_initialized():
            raise MT5InitializeFailedError("Adapter not initialized for modify_position.")
        self._assert_demo_hedging()

        existing = self.positions_get(ticket=ticket)
        if not existing:
            return Mt5MutationResultDTO(
                ticket=ticket, operation="MODIFY_POSITION", retcode=10013,
                retcode_name="TRADE_RETCODE_INVALID", is_success=False,
                comment=f"Position {ticket} not present at broker."
            )
        current = existing[0]

        request_dict = {
            "action": mt5.TRADE_ACTION_SLTP,
            "position": int(ticket),
            "symbol": current.symbol,
            "sl": float(sl),
            "tp": float(tp if tp is not None else (current.take_profit or 0)),
        }
        return self._send_and_classify(request_dict, ticket, "MODIFY_POSITION")

    def close_position(self, ticket: int, volume: Optional[Decimal] = None) -> Mt5MutationResultDTO:
        if not HAS_MT5_PACKAGE or not self.is_initialized():
            raise MT5InitializeFailedError("Adapter not initialized for close_position.")
        self._assert_demo_hedging()

        existing = self.positions_get(ticket=ticket)
        if not existing:
            return Mt5MutationResultDTO(
                ticket=ticket, operation="CLOSE_POSITION", retcode=10013,
                retcode_name="TRADE_RETCODE_INVALID", is_success=False,
                comment=f"Position {ticket} not present at broker."
            )
        current = existing[0]
        close_volume = volume if volume is not None else current.volume
        if close_volume > current.volume:
            return Mt5MutationResultDTO(
                ticket=ticket, operation="CLOSE_POSITION", retcode=10014,
                retcode_name="TRADE_RETCODE_INVALID_VOLUME", is_success=False,
                comment=f"Close volume {close_volume} exceeds position volume {current.volume}."
            )

        tick = self.symbol_tick(current.symbol)
        if tick is None:
            return Mt5MutationResultDTO(
                ticket=ticket, operation="CLOSE_POSITION", retcode=10021,
                retcode_name="TRADE_RETCODE_NO_QUOTES", is_success=False,
                comment="No quote available to price the closing deal."
            )

        # Closing a hedged position means sending the opposite deal against it.
        if current.position_type == "BUY":
            close_type, close_price = mt5.ORDER_TYPE_SELL, float(tick.bid)
        else:
            close_type, close_price = mt5.ORDER_TYPE_BUY, float(tick.ask)

        request_dict = {
            "action": mt5.TRADE_ACTION_DEAL,
            "position": int(ticket),
            "symbol": current.symbol,
            "volume": float(close_volume),
            "type": close_type,
            "price": close_price,
            "deviation": 20,
            "magic": current.magic_number,
            "comment": "close",
            "type_filling": mt5.ORDER_FILLING_IOC,
            "type_time": mt5.ORDER_TIME_GTC,
        }
        result = self._send_and_classify(request_dict, ticket, "CLOSE_POSITION")
        if result.is_success:
            result.closed_volume = close_volume
        return result

    # -- Market data & history ---------------------------------------------

    def symbol_tick(self, symbol: str = CANONICAL_SYMBOL_XAUUSD) -> Optional[Mt5TickDTO]:
        if not HAS_MT5_PACKAGE:
            return None
        resolved = symbol
        if symbol == CANONICAL_SYMBOL_XAUUSD:
            resolution = self.resolve_symbol()
            if resolution.is_resolved:
                resolved = resolution.broker_symbol
        tick = mt5.symbol_info_tick(resolved)
        if tick is None or not getattr(tick, "bid", 0) or not getattr(tick, "ask", 0):
            return None
        return Mt5TickDTO(
            symbol=resolved,
            bid=Decimal(str(tick.bid)),
            ask=Decimal(str(tick.ask)),
        )

    def history_orders_get(self, magic_number: Optional[int] = None, limit: int = 100) -> List[Mt5HistoryOrderDTO]:
        if not HAS_MT5_PACKAGE or not self.is_initialized():
            return []
        from datetime import timedelta
        now = datetime.now(timezone.utc)
        orders = mt5.history_orders_get(now - timedelta(days=30), now)
        if not orders:
            return []
        res: List[Mt5HistoryOrderDTO] = []
        for o in orders:
            if magic_number is not None and getattr(o, "magic", None) != magic_number:
                continue
            res.append(Mt5HistoryOrderDTO(
                ticket=int(o.ticket),
                magic_number=int(getattr(o, "magic", 0)),
                symbol=str(o.symbol),
                order_type="BUY_LIMIT" if getattr(o, "type", None) == mt5.ORDER_TYPE_BUY_LIMIT else "SELL_LIMIT",
                volume=Decimal(str(getattr(o, "volume_initial", 0))),
                price=Decimal(str(getattr(o, "price_open", 0))),
                state="HISTORY",
                comment=str(getattr(o, "comment", "") or ""),
            ))
        return res[:limit]

    def get_status(self) -> Mt5StatusDTO:
        if not self._initialized:
            return Mt5StatusDTO(adapter_mode=MODE_REAL, health_state=self._health_state)
        acc = self.account_info()
        return Mt5StatusDTO(
            adapter_mode=MODE_REAL,
            health_state=self._health_state,
            execution_enabled=True,
            demo_only=True,
            live_execution_enabled=False,
            trading_enabled=self.is_initialized(),
            account_connected=self.is_initialized(),
            account_environment=acc.environment_kind,
            margin_mode=acc.margin_mode,
            resolved_symbol=CANONICAL_SYMBOL_XAUUSD
        )
