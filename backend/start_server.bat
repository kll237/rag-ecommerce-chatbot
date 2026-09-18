@echo off
chcp 65001 >nul
echo ============================================
echo 电商RAG客服系统 - 一键初始化和启动脚本
echo ============================================
echo.

cd /d "%~dp0"

REM 步骤1: 检查Python环境
echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)
echo ✅ Python环境检查通过

REM 步骤2: 初始化数据库和商品数据
echo.
echo [2/4] 初始化数据库和商品数据...
python init_all.py
if errorlevel 1 (
    echo ❌ 数据库初始化失败
    pause
    exit /b 1
)

REM 步骤3: 停止旧的服务进程
echo.
echo [3/4] 停止旧的服务进程...
for /f "tokens=2" %%i in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo 停止进程 %%i
    taskkill /F /PID %%i >nul 2>&1
)
echo ✅ 已清理旧进程

REM 步骤4: 启动后端服务
echo.
echo [4/4] 启动后端服务...
echo ============================================
echo 后端服务启动中...
echo 访问地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo ============================================
echo.
echo 提示: 按 Ctrl+C 停止服务
echo.

python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

pause
