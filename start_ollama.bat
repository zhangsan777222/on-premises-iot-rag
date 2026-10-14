@echo off
REM ============================================================
REM  Start local Ollama service for on-premises RAG deployment
REM  Models live on D: (migrated out of C:)
REM ============================================================
setlocal

set "OLLAMA_EXE=D:\on premises deployment\ollama-app\ollama.exe"
set "OLLAMA_MODELS=D:\on premises deployment\ollama-models"
set "OLLAMA_MAX_LOADED_MODELS=2"
set "OLLAMA_KEEP_ALIVE=30m"
set "OLLAMA_NUM_PARALLEL=1"

if not exist "%OLLAMA_EXE%" (
  echo [ERROR] Ollama not found at: %OLLAMA_EXE%
  pause
  exit /b 1
)

echo ============================================================
echo  Ollama service starting
echo  Program : %OLLAMA_EXE%
echo  Models  : %OLLAMA_MODELS%
echo  KeepAlive: %OLLAMA_KEEP_ALIVE%
echo ============================================================
echo.
echo Press Ctrl+C to stop the service.
echo.

"%OLLAMA_EXE%" serve

endlocal
pause
