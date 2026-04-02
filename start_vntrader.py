# -*- coding: utf-8 -*-
"""VN Trader 启动器"""
import subprocess
import sys
import os

# 切换到脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 检查 MongoDB
try:
    result = subprocess.run(['tasklist'], capture_output=True, text=True)
    if 'mongod' not in result.stdout.lower():
        print("⚠️ MongoDB 未运行，尝试启动...")
        subprocess.run(['net', 'start', 'MongoDB'], capture_output=True)
except:
    pass

# 配置信息
print("=" * 50)
print("VN Trader 启动")
print("=" * 50)
print("\n当前配置：")
print("  MongoDB: 127.0.0.1:27017")
print("  CTP账号: 666857")
print("  行情服务器: tcp://180.169.101.177:43213")
print("  交易服务器: tcp://180.169.101.177:43205")
print("=" * 50)

# 启动
python_exe = os.path.join(script_dir, "vnstudio", "python.exe")
itrader = os.path.join(script_dir, "itrader.py")

print("\n🚀 启动 VN Trader...")
subprocess.Popen([python_exe, itrader])