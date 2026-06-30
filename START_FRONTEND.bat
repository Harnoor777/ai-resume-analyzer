@echo off
echo ========================================
echo   Starting AI Resume Analyzer Frontend
echo ========================================
echo.

cd frontend

echo Starting web server on port 3000...
echo.
echo ========================================
echo   Frontend is running!
echo   URL: http://localhost:3000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python -m http.server 3000

pause
