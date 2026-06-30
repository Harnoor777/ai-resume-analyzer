@echo off
echo ========================================
echo   Starting AI Resume Analyzer Backend
echo ========================================
echo.

REM Activate virtual environment
echo [1/4] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment!
    echo Make sure venv folder exists. Run: python -m venv venv
    pause
    exit /b 1
)
echo Done.
echo.

REM Check database connection
echo [2/4] Checking database connection...
python -c "import psycopg2; conn = psycopg2.connect('postgresql://postgres:noor%%40123@localhost:5432/resume_analyzer'); print('Database connection OK'); conn.close()"
if errorlevel 1 (
    echo ERROR: Cannot connect to database!
    echo.
    echo Please check:
    echo 1. PostgreSQL is running
    echo 2. Database 'resume_analyzer' exists
    echo 3. Password is correct in .env file
    echo.
    pause
    exit /b 1
)
echo Done.
echo.

REM Initialize database tables
echo [3/4] Initializing database tables...
python backend/database/database.py
if errorlevel 1 (
    echo ERROR: Could not initialize database!
    pause
    exit /b 1
)
echo Done.
echo.

REM Start the backend server
echo [4/4] Starting FastAPI backend server...
echo.
echo ========================================
echo   Backend is starting...
echo   URL: http://localhost:8000
echo   API Docs: http://localhost:8000/docs
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

venv\Scripts\python.exe backend/main.py

pause
