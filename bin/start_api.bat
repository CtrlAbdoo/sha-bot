@echo off
setlocal enabledelayedexpansion
echo ===== OpenRouter Chatbot API Launcher =====
echo.

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not found in your PATH.
    echo Please install Python and make sure it's added to your PATH.
    pause
    exit /b 1
)

REM Check for required directories
if not exist "..\app" (
    echo Creating app directory structure...
    mkdir ..\app
    mkdir ..\logs
    mkdir ..\tests
)

REM Check if required packages are installed
python -c "import fastapi, uvicorn, dotenv, pymongo, loguru" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing required packages...
    pip install -r ..\requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to install requirements.
        echo Please run: pip install -r ..\requirements.txt
        pause
        exit /b 1
    )
)

REM Check for .env file and API key
if not exist "..\.env" (
    echo No .env file found.
    echo Running API key setup...
    python ..\scripts\setup_api_key.py
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to set up API key.
        pause
        exit /b 1
    )
) else (
    REM Check for API key in .env file
    findstr /c:"OPENROUTER_API_KEY" ..\.env >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo No API key found in .env file.
        echo Running API key setup...
        python ..\scripts\setup_api_key.py
        if %ERRORLEVEL% NEQ 0 (
            echo Failed to set up API key.
            pause
            exit /b 1
        )
    )
)

REM Start the API server
echo.
echo Starting the API server with fine-tuned simulation...
echo Press Ctrl+C to stop the server.
echo.

cd ..
python -m uvicorn app.finetuned_api:app --host 0.0.0.0 --port 8000 