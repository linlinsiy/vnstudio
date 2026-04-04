# -*- coding: utf-8 -*-
"""VN Trader GUI startup wrapper."""

import json
import os
import subprocess


def load_ctp_setting() -> dict:
    path = os.path.expanduser("~/.vntrader/connect_ctp.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    try:
        result = subprocess.run(["tasklist"], capture_output=True, text=True)
        if "mongod" not in result.stdout.lower():
            print("[!] MongoDB is not running, trying to start service...")
            subprocess.run(["net", "start", "MongoDB"], capture_output=True)
    except Exception:
        pass

    try:
        ctp_setting = load_ctp_setting()
    except Exception as e:
        print(f"[X] Failed to load CTP config: {e}")
        return

    print("=" * 50)
    print("VN Trader GUI Startup")
    print("=" * 50)
    print("Current CTP config:")
    print(f"  Broker: {ctp_setting.get('经纪商代码', '')}")
    print(f"  User: {ctp_setting.get('用户名', '')}")
    print(f"  Market Front: {ctp_setting.get('行情服务器', '')}")
    print(f"  Trade Front: {ctp_setting.get('交易服务器', '')}")
    print("=" * 50)

    python_exe = os.path.join(script_dir, "vnstudio", "python.exe")
    itrader = os.path.join(script_dir, "itrader.py")

    print("Launching VN Trader GUI...")
    subprocess.Popen([python_exe, itrader])


if __name__ == "__main__":
    main()
