@echo off
title Push Instagram Agent to GitHub (@harekrusna65-max)
cd /d "D:\instagram agent"
echo ==================================================
echo      PUSHING INSTAGRAM AGENT TO GITHUB
echo ==================================================
echo Repository: https://github.com/harekrusna65-max/instagram-agent.git
echo.
echo [*] Pushing code to GitHub...
echo [!] Agar browser popup khule, toh bas "Sign in with your browser" par Authorize click kijiye.
echo.
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ==================================================
    echo [✓ SUCCESS] Code pushed to GitHub successfully!
    echo ==================================================
) else (
    echo.
    echo [!] Push failed. Check your GitHub permissions or credentials.
)
pause
