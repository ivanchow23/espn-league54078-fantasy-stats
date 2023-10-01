set SCRIPT_DIR=%~dp0
set VENV_PATH=%SCRIPT_DIR%.venv
set VENV_PYTHON_EXE=%VENV_PATH%\Scripts\python.exe

:: Create virtual environment
python -m venv %VENV_PATH%

:: Install packages to virtual environment
%VENV_PYTHON_EXE% -m pip install -r %SCRIPT_DIR%requirements.txt

pause