@echo off
echo ========================================
echo   System Check for AI Resume Analyzer
echo ========================================
echo.

REM Check Python
echo [1/6] Checking Python installation...
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    set HAS_ERROR=1
) else (
    echo OK - Python found
)
echo.

REM Check virtual environment
echo [2/6] Checking virtual environment...
if exist "venv\Scripts\activate.bat" (
    echo OK - Virtual environment exists
) else (
    echo ERROR: Virtual environment not found!
    echo Run: python -m venv venv
    set HAS_ERROR=1
)
echo.

REM Check if venv has packages
echo [3/6] Checking installed packages...
call venv\Scripts\activate.bat 2>nul
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo ERROR: Required packages not installed!
    echo Run: pip install -r requirements.txt
    set HAS_ERROR=1
) else (
    echo OK - FastAPI is installed
)
echo.

REM Check .env file
echo [4/6] Checking .env configuration...
if exist ".env" (
    echo OK - .env file exists
    findstr /C:"DATABASE_URL" .env >nul
    if errorlevel 1 (
        echo WARNING: DATABASE_URL not found in .env
        set HAS_ERROR=1
    )
) else (
    echo ERROR: .env file not found!
    echo Copy .env.example to .env
    set HAS_ERROR=1
)
echo.

REM Check PostgreSQL connection
echo [5/6] Checking PostgreSQL connection...
python -c "import psycopg2; conn = psycopg2.connect('postgresql://postgres:noor%%40123@localhost:5432/resume_analyzer'); print('OK - Database connection successful'); conn.close()" 2>nul
if errorlevel 1 (
    echo ERROR: Cannot connect to PostgreSQL database!
    echo.
    echo Possible issues:
    echo - PostgreSQL service is not running
    echo - Database 'resume_analyzer' does not exist
    echo - Wrong password in .env file
    echo - PostgreSQL not listening on localhost:5432
    set HAS_ERROR=1
)
echo.

REM Check if backend/frontend directories exist
echo [6/6] Checking project structure...
if exist "backend\main.py" (
    echo OK - Backend files found
) else (
    echo ERROR: backend\main.py not found!
    set HAS_ERROR=1
)
if exist "frontend\index.html" (
    echo OK - Frontend files found
) else (
    echo ERROR: frontend\index.html not found!
    set HAS_ERROR=1
)
echo.

echo ========================================
if defined HAS_ERROR (
    echo   STATUS: FAILED - Please fix errors above
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Fix the errors listed above
    echo 2. Run this script again
    echo 3. Then run START_BACKEND.bat
) else (
    echo   STATUS: ALL CHECKS PASSED!
    echo ========================================
    echo.
    echo You're ready to start the application!
    echo.
    echo Next steps:
    echo 1. Run START_BACKEND.bat in this window
    echo 2. Open a new terminal and run START_FRONTEND.bat
    echo 3. Open http://localhost:3000 in your browser
)
echo.

pause
