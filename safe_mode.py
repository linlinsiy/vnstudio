# -*- coding: utf-8 -*-
"""Read-only trading guard for local strategy debugging."""

from types import MethodType


def enable_read_only_mode(main_engine):
    """
    Block all order and cancel requests while keeping market data active.

    This is intended for safe local debugging against production/front
    environments where receiving ticks is required but real trading must
    never be triggered.
    """

    original_send_order = main_engine.send_order
    original_send_orders = main_engine.send_orders
    original_cancel_order = main_engine.cancel_order
    original_cancel_orders = main_engine.cancel_orders

    def blocked_send_order(self, req, gateway_name):
        self.write_log(
            f"[安全模式] 已拦截委托发送: {req.symbol}.{req.exchange.value} "
            f"{req.direction.value} {req.offset.value} "
            f"price={req.price} volume={req.volume}",
            gateway_name,
        )
        return ""

    def blocked_send_orders(self, reqs, gateway_name):
        for req in reqs:
            self.write_log(
                f"[安全模式] 已拦截批量委托: {req.symbol}.{req.exchange.value} "
                f"{req.direction.value} {req.offset.value} "
                f"price={req.price} volume={req.volume}",
                gateway_name,
            )
        return ["" for _ in reqs]

    def blocked_cancel_order(self, req, gateway_name):
        self.write_log(
            f"[安全模式] 已拦截撤单: order_ref={req.orderid}",
            gateway_name,
        )

    def blocked_cancel_orders(self, reqs, gateway_name):
        for req in reqs:
            self.write_log(
                f"[安全模式] 已拦截批量撤单: order_ref={req.orderid}",
                gateway_name,
            )

    main_engine.send_order = MethodType(blocked_send_order, main_engine)
    main_engine.send_orders = MethodType(blocked_send_orders, main_engine)
    main_engine.cancel_order = MethodType(blocked_cancel_order, main_engine)
    main_engine.cancel_orders = MethodType(blocked_cancel_orders, main_engine)
    main_engine.read_only_mode = True
    main_engine._original_send_order = original_send_order
    main_engine._original_send_orders = original_send_orders
    main_engine._original_cancel_order = original_cancel_order
    main_engine._original_cancel_orders = original_cancel_orders

    main_engine.write_log("已启用安全联调模式: 仅接收行情，禁止所有下单和撤单")
    return main_engine
