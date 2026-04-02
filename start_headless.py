# -*- coding: utf-8 -*-
"""
VN Trader 无头启动脚本 - 无需 GUI，直接后台运行数据记录和策略
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from time import sleep
from datetime import datetime

from vnpy.event import EventEngine
from vnpy.trader.engine import MainEngine
from vnpy.gateway.ctp import CtpGateway
from vnpy.trader.object import SubscribeRequest
from vnpy.trader.constant import Exchange

from vnpy.app.cta_strategy import CtaStrategyApp
from vnpy.app.data_recorder import DataRecorderApp

# CTP 配置
CTP_SETTING = {
    "用户名": "666857",
    "密码": "690522",
    "经纪商代码": "66666",
    "交易服务器": "tcp://180.169.101.177:43205",
    "行情服务器": "tcp://180.169.101.177:43213",
    "产品名称": "client_itrader_1.1.1.1",
    "授权编码": "6BQKCO5WBK213AXI",
    "产品信息": ""
}

def main():
    print("=" * 50)
    print("VN Trader 无头模式启动")
    print("=" * 50)
    print(f"时间: {datetime.now()}")
    print()
    
    # 创建事件引擎
    event_engine = EventEngine()
    event_engine.start()
    print("[✓] 事件引擎启动")
    
    # 创建主引擎
    main_engine = MainEngine(event_engine)
    print("[✓] 主引擎启动")
    
    # 添加 CTP 网关
    main_engine.add_gateway(CtpGateway)
    print("[✓] CTP 网关加载")
    
    # 添加应用
    cta_engine = main_engine.add_app(CtaStrategyApp)
    recorder_engine = main_engine.add_app(DataRecorderApp)
    print("[✓] CTA 策略模块加载")
    print("[✓] 数据记录模块加载")
    
    # 连接 CTP
    print()
    print("正在连接 CTP...")
    try:
        main_engine.connect(CTP_SETTING, "CTP")
        print("[✓] CTP 连接请求已发送")
    except Exception as e:
        print(f"[✗] CTP 连接失败: {e}")
        return
    
    # 等待连接建立
    print("等待 5 秒让连接建立...")
    sleep(5)
    
    # 检查连接状态
    print()
    print("当前状态:")
    print(f"  网关: {main_engine.get_all_gateway_names()}")
    
    # 启动数据记录（从配置文件读取）
    print()
    print("启动数据记录...")
    try:
        import json
        with open(os.path.expanduser("~/.vntrader/data_recorder_setting.json"), "r", encoding="utf-8") as f:
            settings = json.load(f)
        
        for vt_symbol in settings.get("bar", {}):
            recorder_engine.add_bar_recording(vt_symbol)
            print(f"  [+] K线记录: {vt_symbol}")
    except Exception as e:
        print(f"  [!] 数据记录启动警告: {e}")
    
    # 启动 CTA 策略
    print()
    print("启动 CTA 策略...")
    try:
        cta_engine.init_all_strategies()
        sleep(2)
        cta_engine.start_all_strategies()
        print("[✓] 所有策略已启动")
    except Exception as e:
        print(f"[✗] 策略启动失败: {e}")
    
    print()
    print("=" * 50)
    print("VN Trader 运行中...")
    print("按 Ctrl+C 停止")
    print("=" * 50)
    
    # 保持运行
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print()
        print("正在关闭...")
        main_engine.close()
        event_engine.stop()
        print("[✓] 已安全退出")

if __name__ == "__main__":
    main()
