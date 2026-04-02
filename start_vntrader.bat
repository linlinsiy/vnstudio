@echo off
chcp 65001 >nul
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
echo ========================================
echo VN Trader 启动脚本
echo ========================================
echo.
echo 正在检查 MongoDB 服务...
tasklist | findstr /i "mongod" >nul
if errorlevel 1 (
    echo [警告] MongoDB 未运行，尝试启动...
    net start MongoDB 2>nul
    timeout /t 2 >nul
)

echo.
echo 当前配置信息：
echo ----------------------------------------
echo MongoDB: 127.0.0.1:27017 (本地无认证)
echo CTP账号: 666857
echo 行情服务器: tcp://180.169.101.177:43213
echo 交易服务器: tcp://180.169.101.177:43205
echo ----------------------------------------
echo.
echo 启动 VN Trader...
echo.

cd /d "%~dp0"
"%~dp0vnstudio\python.exe" "%~dp0itrader.py"

if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出，按任意键关闭...
    pause >nul
)
