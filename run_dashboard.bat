@echo off
title AI Beauty & Fashion Marketing Agent
cd /d "F:\Projects\beauty-marketing-agent"
echo ========================================================
echo   AI Beauty & Fashion Marketing Agent - 100%% Free Stack
echo ========================================================
echo Starting local web server...
start http://127.0.0.1:8000
py -m uvicorn backend.server:app --host 127.0.0.1 --port 8000
pause
