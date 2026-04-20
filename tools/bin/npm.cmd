@ECHO OFF
SETLOCAL

SET "NODE_EXE=C:\Program Files\nodejs\node.exe"
IF NOT EXIST "%NODE_EXE%" (
  SET "NODE_EXE=C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Microsoft\VisualStudio\NodeJs\node.exe"
)
IF NOT EXIST "%NODE_EXE%" (
  SET "NODE_EXE=C:\Users\IOT\.lmstudio\.internal\utils\node.exe"
)
IF NOT EXIST "%NODE_EXE%" (
  ECHO No working Node.js runtime found for repo-local npm wrapper.
  EXIT /B 1
)

SET "NPM_CLI_JS=C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js"
IF NOT EXIST "%NPM_CLI_JS%" (
  ECHO npm CLI not found at "%NPM_CLI_JS%".
  EXIT /B 1
)

SET "NPM_CONFIG_CACHE=C:\Users\IOT\AppData\Local\npm-cache"
SET "TEMP=C:\Users\IOT\AppData\Local\Temp"
SET "TMP=C:\Users\IOT\AppData\Local\Temp"
SET "SystemRoot=C:\Windows"
SET "windir=C:\Windows"
SET "ComSpec=C:\Windows\System32\cmd.exe"

"%NODE_EXE%" "%NPM_CLI_JS%" %*
