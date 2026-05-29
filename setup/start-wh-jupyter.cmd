@echo off
REM Launches Jupyter inside WSL Ubuntu so the WH notebook can use pyscf.
REM Notebooks live in this Windows folder; only the Python kernel runs in WSL.
REM Press Ctrl+C in this window to stop the server.
REM
REM Assumptions:
REM   1. WSL2 is installed with an Ubuntu distribution (default: Ubuntu-24.04).
REM      Override with: set WSL_DISTRO=Ubuntu-22.04
REM   2. You created a venv at ~/quantum-wsl/.venv inside that distribution
REM      and installed requirements-wsl.txt into it.
REM   3. Run this script from the repo root (cd into quantum-fusion-poc/
REM      first). The current Windows directory becomes the Jupyter
REM      notebook-dir so the browser sees the repo files.

if "%WSL_DISTRO%"=="" set WSL_DISTRO=Ubuntu-24.04

REM Reject UNC paths up front. They'd show up as \\server\share\... in
REM %CD% and wslpath cannot meaningfully translate them.
echo %CD% | findstr /b /c:"\\\\" >nul
if not errorlevel 1 (
    echo ERROR: This script does not support UNC paths ^(\\server\share^).
    echo        Map the share to a drive letter first, then run again.
    exit /b 1
)

REM Pass the Windows working directory through WSLENV so wsl/bash sees it
REM as an environment variable. The /p flag tells WSL to translate the
REM value from Windows path notation to /mnt/<drive>/... on the way in,
REM which is both faster and more robust than string substitution and
REM handles drive letters, spaces, and unusual characters cleanly.
set "WIN_CWD=%CD%"
set "WSLENV=WIN_CWD/p"

echo Starting Jupyter inside WSL %WSL_DISTRO%...
echo   Windows working dir: %CD%
echo Open the URL it prints in your Windows browser.
echo.

REM %WSL_DISTRO% is quoted in case someone sets a distro name with spaces.
REM Inside bash, $WIN_CWD is already in WSL path form (thanks to WSLENV/p)
REM and is quoted with double-quotes to tolerate paths containing spaces
REM and apostrophes.
wsl -d "%WSL_DISTRO%" -e bash -lc "cd ~/quantum-wsl && .venv/bin/jupyter notebook --allow-root --no-browser --ip=127.0.0.1 --port=8888 --notebook-dir=\"$WIN_CWD\""
