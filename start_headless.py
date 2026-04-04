# -*- coding: utf-8 -*-
"""
VN Trader headless startup script.

This script runs CTP connection, data recorder, and CTA strategy apps
without launching the Qt GUI.
"""

import json
import os
import sys
from datetime import datetime
from time import sleep

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.gateway.ctp import CtpGateway

from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.data_recorder import DataRecorderApp

from safe_mode import enable_read_only_mode


def load_json_config(filename: str) -> dict:
    """Load one vn.py runtime config file from ~/.vntrader."""
    path = os.path.expanduser(f"~/.vntrader/{filename}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=" * 50)
    print("VN Trader Headless Startup")
    print("=" * 50)
    print(f"Time: {datetime.now()}")
    print()

    try:
        ctp_setting = load_json_config("connect_ctp.json")
    except Exception as e:
        print(f"[X] Failed to load CTP config: {e}")
        return

    print("Current CTP config:")
    print(f"  Broker: {ctp_setting.get('经纪商代码', '')}")
    print(f"  User: {ctp_setting.get('用户名', '')}")
    print(f"  Market Front: {ctp_setting.get('行情服务器', '')}")
    print(f"  Trade Front: {ctp_setting.get('交易服务器', '')}")
    print(
        "  Product Name: "
        f"{ctp_setting.get('产品名称', '') or '<empty>'}"
    )
    print(
        "  Auth Code: "
        f"{ctp_setting.get('授权编码', '') or '<empty>'}"
    )
    print()

    missing = [
        key for key in ("产品名称", "授权编码")
        if not ctp_setting.get(key)
    ]
    if missing:
        print("[!] Missing likely-required CTP fields: " + ", ".join(missing))
        print("[!] Many CTP environments require both 产品名称 and 授权编码.")
        print()

    event_engine = EventEngine()
    print("[+] Event engine created")

    main_engine = MainEngine(event_engine)
    enable_read_only_mode(main_engine)
    print("[+] Main engine started")
    print("[+] Read-only trading guard enabled")

    main_engine.add_gateway(CtpGateway)
    print("[+] CTP gateway loaded")

    cta_engine = main_engine.add_app(CtaStrategyApp)
    recorder_engine = main_engine.add_app(DataRecorderApp)
    print("[+] CTA app loaded")
    print("[+] Data recorder app loaded")

    print()
    print("Connecting to CTP...")
    try:
        main_engine.connect(ctp_setting, "CTP")
        print("[+] CTP connect request sent")
    except Exception as e:
        print(f"[X] CTP connect failed: {e}")
        return

    print("Waiting 5 seconds for CTP connection...")
    sleep(5)

    print()
    print("Current status:")
    print(f"  Gateways: {main_engine.get_all_gateway_names()}")

    print()
    print("Starting data recorder...")
    try:
        settings = load_json_config("data_recorder_setting.json")
        for vt_symbol in settings.get("bar", {}):
            recorder_engine.add_bar_recording(vt_symbol)
            print(f"  [+] Bar recording: {vt_symbol}")
    except Exception as e:
        print(f"  [!] Data recorder warning: {e}")

    print()
    print("Starting CTA strategies...")
    try:
        cta_engine.init_all_strategies()
        sleep(2)
        cta_engine.start_all_strategies()
        print("[+] All strategies started")
    except Exception as e:
        print(f"[X] Strategy startup failed: {e}")

    print()
    print("=" * 50)
    print("VN Trader is running")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print()
        print("Shutting down...")
        main_engine.close()
        event_engine.stop()
        print("[+] Shutdown complete")


if __name__ == "__main__":
    main()
