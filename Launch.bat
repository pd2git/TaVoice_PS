@ECHO OFF
ECHO 改变当前活动代码页为UTF-8
ECHO Change the current activity code page to UTF-8
@CHCP 65001
title XX的语音

SET BASE_DIR=%~dp0

ECHO 工作目录：%BASE_DIR%
ECHO Work directory：%BASE_DIR%
CD %BASE_DIR%

ECHO 启动主程序...
ECHO Starting the main program...
:restart
python -u server.py
echo -----------------------------Restarting---------------------------------------
rem goto restart
pause
EXIT