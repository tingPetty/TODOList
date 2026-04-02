@echo off
setlocal
cd /d "%~dp0"
if exist "D:\anaconda3\condabin\conda.bat" (
	call "D:\anaconda3\condabin\conda.bat" run -n todo_desk pythonw "%~dp0main.py"
) else (
	conda run -n todo_desk pythonw "%~dp0main.py"
)
endlocal
