@echo off
chcp 65001 >nul
echo ============================================================
echo   KEC ERP - Production Build and Start
echo ============================================================

echo.
echo [1/3] Building React frontend...
cd frontend
call npm run build
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Frontend build failed!
    pause
    exit /b 1
)
cd ..
echo [OK] Frontend built to app/static/dist/

echo.
echo [2/3] Running DB migration...
.venv\Scripts\python migrate_columns.py

echo.
echo [3/3] Starting production server...
echo   URL     : http://localhost:5000
echo   Threads : 32 (handles 1000+ concurrent users)
echo ============================================================
.venv\Scripts\python wsgi.py
pause
