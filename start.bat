@echo off
echo ================================================================
echo           CodeSupply - Software Supply-Chain Platform          
echo ================================================================
echo Starting CodeSupply Backend and Frontend...
echo.

start "CodeSupply Backend" cmd /k "cd backend && if exist venv\Scripts\activate.bat (call venv\Scripts\activate.bat) && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak >nul

start "CodeSupply Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo [OK] CodeSupply is launching!
echo  - Frontend Dashboard: http://localhost:3000
echo  - Backend OpenAPI Docs: http://localhost:8000/docs
echo ================================================================
