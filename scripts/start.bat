@echo off
set PYTHONPATH=%~dp0..;%PYTHONPATH%

set env_python_exe=%~dp0..\env\python.exe

if exist     %env_python_exe%  set command=%env_python_exe% -m pip_repo_manager %*

echo %command%
call %command%
