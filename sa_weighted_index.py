from datetime import timedelta
import re
from typing import Dict, List

from vnpy.event import Event
from vnpy.trader.constant import Exchange, Product
from vnpy.trader.engine import BaseEngine, MainEngine
from vnpy.trader.event import EVENT_CONTRACT, EVENT_TICK
from vnpy.trader.object import SubscribeRequest, TickData


APP_NAME = "SaWeightedIndex"

SA_SYMBOL_PATTERN = re.compile(r"^SA\d{3,4}$")


class SaWeightedIndexEngine(BaseEngine):
    """Generate weighted SA index tick as SA_ZS.CZCE from live SA futures ticks."""

    def __init__(self, main_engine: MainEngine, event_engine):
        super().__init__(main_engine, event_engine, APP_NAME)

        self.target_symbol: str = "SA_ZS"
        self.target_exchange: Exchange = Exchange.CZCE
        self.target_vt_symbol: str = f"{self.target_symbol}.{self.target_exchange.value}"
        self.synthetic_gateway: str = "SA_INDEX"

        self.leg_ticks: Dict[str, TickData] = {}
        self.subscribed_legs: Dict[str, str] = {}
        self.synthetic_tick_count: int = 0

        self.register_event()
        self.main_engine.write_log("已启用 SA_ZS 纯碱加权行情引擎", APP_NAME)
        print("[SA_ZS] weighted index engine ready")

    def register_event(self) -> None:
        self.event_engine.register(EVENT_CONTRACT, self.process_contract_event)
        self.event_engine.register(EVENT_TICK, self.process_tick_event)

    def process_contract_event(self, event: Event) -> None:
        contract = event.data

        if contract.exchange != Exchange.CZCE:
            return
        if contract.product != Product.FUTURES:
            return
        if not SA_SYMBOL_PATTERN.match(contract.symbol):
            return
        if contract.vt_symbol in self.subscribed_legs:
            return

        req = SubscribeRequest(symbol=contract.symbol, exchange=contract.exchange)
        self.main_engine.subscribe(req, contract.gateway_name)
        self.subscribed_legs[contract.vt_symbol] = contract.gateway_name

        self.main_engine.write_log(
            f"SA_ZS 订阅纯碱腿合约：{contract.vt_symbol}",
            APP_NAME
        )
        print(f"[SA_ZS] subscribed leg: {contract.vt_symbol}")

    def process_tick_event(self, event: Event) -> None:
        tick: TickData = event.data

        if tick.symbol == self.target_symbol:
            return
        if tick.exchange != Exchange.CZCE:
            return
        if not SA_SYMBOL_PATTERN.match(tick.symbol):
            return

        self.leg_ticks[tick.vt_symbol] = tick

        weighted_tick = self.generate_weighted_tick(tick)
        if weighted_tick:
            self.synthetic_tick_count += 1
            if self.synthetic_tick_count <= 5:
                print(
                    "[SA_ZS] synthetic tick "
                    f"{self.synthetic_tick_count}: dt={weighted_tick.datetime} "
                    f"last={weighted_tick.last_price:.2f} "
                    f"oi={weighted_tick.open_interest:.0f}"
                )
            self.event_engine.put(Event(EVENT_TICK, weighted_tick))

    def generate_weighted_tick(self, trigger_tick: TickData) -> TickData:
        valid_ticks: List[TickData] = []
        freshness_limit = trigger_tick.datetime - timedelta(minutes=5)

        for tick in self.leg_ticks.values():
            if tick.datetime.date() != trigger_tick.datetime.date():
                continue
            if tick.datetime < freshness_limit:
                continue
            if tick.last_price <= 0:
                continue
            if tick.open_interest <= 0:
                continue
            valid_ticks.append(tick)

        if not valid_ticks:
            return None

        total_weight = sum(tick.open_interest for tick in valid_ticks)
        if total_weight <= 0:
            return None

        def weighted_value(field: str, positive_only: bool = False, fallback: float = 0) -> float:
            numerator = 0.0
            denominator = 0.0

            for item in valid_ticks:
                value = getattr(item, field, 0)
                if positive_only and value <= 0:
                    continue

                weight = item.open_interest
                numerator += value * weight
                denominator += weight

            if denominator <= 0:
                return fallback
            return numerator / denominator

        last_price = weighted_value("last_price", positive_only=True)
        if last_price <= 0:
            return None

        bid_price_1 = weighted_value("bid_price_1", positive_only=True, fallback=last_price)
        ask_price_1 = weighted_value("ask_price_1", positive_only=True, fallback=last_price)
        open_price = weighted_value("open_price", positive_only=True, fallback=last_price)
        high_price = weighted_value("high_price", positive_only=True, fallback=last_price)
        low_price = weighted_value("low_price", positive_only=True, fallback=last_price)
        pre_close = weighted_value("pre_close", positive_only=True, fallback=last_price)

        volume = sum(tick.volume for tick in valid_ticks)
        last_volume = sum(tick.last_volume for tick in valid_ticks)
        open_interest = sum(tick.open_interest for tick in valid_ticks)
        bid_volume_1 = sum(tick.bid_volume_1 for tick in valid_ticks if tick.bid_volume_1 > 0)
        ask_volume_1 = sum(tick.ask_volume_1 for tick in valid_ticks if tick.ask_volume_1 > 0)

        weighted_tick = TickData(
            symbol=self.target_symbol,
            exchange=self.target_exchange,
            datetime=trigger_tick.datetime,
            name="纯碱加权",
            volume=volume,
            open_interest=open_interest,
            last_price=last_price,
            last_volume=last_volume,
            open_price=open_price,
            high_price=high_price,
            low_price=low_price,
            pre_close=pre_close,
            bid_price_1=bid_price_1,
            ask_price_1=ask_price_1,
            bid_volume_1=bid_volume_1,
            ask_volume_1=ask_volume_1,
            gateway_name=self.synthetic_gateway,
        )
        return weighted_tick
