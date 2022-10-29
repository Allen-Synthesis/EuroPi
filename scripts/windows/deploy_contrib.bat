::CONTRIB::
rshell mkdir /pyboard/lib/contrib
set "deployfilepath=%~dp0"
set "filepathcontrib=%deployfilepath%..\..\software\contrib\*.py"
set "filepathrshell=%filepathcontrib:\=/%"
set "filepathrshell=%filepathrshell:C:/=/%"
dir "%filepathcontrib%"
cd/
rshell cp %filepathrshell% /pyboard/lib/contrib

cd %~dp0