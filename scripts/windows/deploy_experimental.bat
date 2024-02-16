::EXPERIMENTAL::
rshell mkdir /pyboard/lib/experimental
set "deployfilepath=%~dp0"
set "filepathexperimental=%deployfilepath%..\..\software\firmware\experimental\*.py"
set "filepathrshell=%filepathexperimental:\=/%"
set "filepathrshell=%filepathrshell:C:/=/%"
dir "%filepathexperimental%"
cd/
rshell cp %filepathrshell% /pyboard/lib/experimental

cd %~dp0