::FIRMWARE::
set "deployfilepath=%~dp0"
set "filepathfirmware=%deployfilepath%..\..\software\firmware\*.py"
set "filepathrshell=%filepathfirmware:\=/%"
set "filepathrshell=%filepathrshell:C:/=/%"
dir "%filepathfirmware%"
cd/
rshell mkdir /pyboard/lib
rshell cp %filepathrshell% /pyboard/lib/

cd %~dp0