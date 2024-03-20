call deploy_firmware.bat
call deploy_experimental.bat
call deploy_contrib.bat

rshell cp /pyboard/lib/contrib/menu.py menu.py
ren menu.py main.py
rshell cp main.py /pyboard
del main.py

::Navigate back to original directory::
cd %~dp0