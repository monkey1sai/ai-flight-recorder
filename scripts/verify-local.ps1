param(
    [switch]$FailOnSkip
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

$env:UV_CACHE_DIR = Join-Path $repoRoot ".uv-cache"
$env:CARGO_HOME = Join-Path $repoRoot ".cargo-home"
$env:RUSTUP_HOME = Join-Path $repoRoot ".rustup-home"
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
$pwshCommand = if ($pwsh = Get-Command "pwsh" -ErrorAction SilentlyContinue) {
    $pwsh.Source
} else {
    "pwsh"
}
$npmCommand = if (Test-Path (Join-Path $repoRoot "tools/bin/npm.ps1")) {
    Join-Path $repoRoot "tools/bin/npm.ps1"
} else {
    "npm"
}
$npmRunPrefix = if ($npmCommand -like "*.ps1") {
    @($pwshCommand, "-NoProfile", "-File", $npmCommand)
} else {
    @($npmCommand)
}

$steps = @(
    @{ Name = "Ruff"; Command = @("uv", "run", "ruff", "check", ".") },
    @{ Name = "Mypy"; Command = @("uv", "run", "python", "-m", "mypy", "apps", "packages", "workers", "tests") },
    @{ Name = "Pytest unit"; Command = @("uv", "run", "python", "-m", "pytest", "tests/unit", "-q", "-p", "no:cacheprovider") },
    @{ Name = "Pytest integration"; Command = @("uv", "run", "python", "-m", "pytest", "tests/integration", "-q", "-p", "no:cacheprovider") },
    @{ Name = "Pytest e2e"; Command = @("uv", "run", "python", "-m", "pytest", "tests/e2e", "-q", "-p", "no:cacheprovider") },
    @{ Name = "Pytest smoke"; Command = @("uv", "run", "python", "-m", "pytest", "tests/smoke", "-q", "-p", "no:cacheprovider") },
    @{ Name = "Web lint"; Command = $npmRunPrefix + @("run", "lint", "--workspace", "@aeris/web") },
    @{ Name = "Web typecheck"; Command = $npmRunPrefix + @("run", "typecheck", "--workspace", "@aeris/web") },
    @{ Name = "Cargo check"; Command = @("cargo", "check", "--manifest-path", "edge/daemon/Cargo.toml") },
    @{ Name = "Docker compose config"; Command = @("docker-compose", "-f", "infra/compose/docker-compose.yml", "config"); AlternateCommand = @("docker", "compose", "-f", "infra/compose/docker-compose.yml", "config") }
)

$failed = @()
$skipped = @()

function Test-Executable {
    param([string]$Name)

    if (Test-Path -LiteralPath $Name) {
        return $true
    }

    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

foreach ($step in $steps) {
    $exe = $step.Command[0]
    $commandToRun = $step.Command

    if (-not (Test-Executable $exe)) {
        if ($step.ContainsKey("AlternateCommand") -and (Test-Executable $step.AlternateCommand[0])) {
            $commandToRun = $step.AlternateCommand
        } else {
            Write-Host "[SKIP] $($step.Name): missing executable '$exe'"
            $skipped += $step.Name
            continue
        }
    }

    Write-Host "[RUN ] $($step.Name): $($commandToRun -join ' ')"
    & $commandToRun[0] @($commandToRun[1..($commandToRun.Length - 1)])
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] $($step.Name)"
        $failed += $step.Name
    } else {
        Write-Host "[PASS] $($step.Name)"
    }
}

Write-Host ""
Write-Host "Summary"
Write-Host "Passed: $($steps.Count - $failed.Count - $skipped.Count)"
Write-Host "Failed: $($failed.Count)"
Write-Host "Skipped: $($skipped.Count)"

if ($failed.Count -gt 0) {
    exit 1
}

if ($FailOnSkip -and $skipped.Count -gt 0) {
    exit 2
}

exit 0
