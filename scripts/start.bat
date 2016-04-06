@echo off
set PYTHONPATH=%~dp0..;%PYTHONPATH%

set venv_python_exe=%~dp0..\venv\Scripts\python.exe
set env_python_exe=%~dp0..\env\python.exe

if exist     %venv_python_exe% set command=%venv_python_exe% -m pip_repo_manager %*
if exist     %env_python_exe%  set command=%env_python_exe% -m pip_repo_manager %*

echo %command%
call %command%

pause
