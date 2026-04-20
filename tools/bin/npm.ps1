Set-StrictMode -Version Latest

$nodeCandidates = @(
    'C:\Program Files\nodejs\node.exe',
    'C:\Program Files\Microsoft Visual Studio\2022\Professional\MSBuild\Microsoft\VisualStudio\NodeJs\node.exe',
    'C:\Users\IOT\.lmstudio\.internal\utils\node.exe'
)

$nodeExe = $nodeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $nodeExe) {
    throw 'No working Node.js runtime found for repo-local npm wrapper.'
}

$npmCli = 'C:\Program Files\nodejs\node_modules\npm\bin\npm-cli.js'
if (-not (Test-Path $npmCli)) {
    throw "npm CLI not found at $npmCli."
}

$env:NPM_CONFIG_CACHE = 'C:\Users\IOT\AppData\Local\npm-cache'
$env:TEMP = 'C:\Users\IOT\AppData\Local\Temp'
$env:TMP = 'C:\Users\IOT\AppData\Local\Temp'
$env:SystemRoot = 'C:\Windows'
$env:windir = 'C:\Windows'
$env:ComSpec = 'C:\Windows\System32\cmd.exe'

if ($MyInvocation.ExpectingInput) {
    $input | & $nodeExe $npmCli $args
} else {
    & $nodeExe $npmCli $args
}

exit $LASTEXITCODE
