# PowerShell wrapper for deploy/deploy.sh (needs Git for Windows).
#   .\deploy\deploy.ps1               deploy
#   .\deploy\deploy.ps1 --rollback    go back one release
#   .\deploy\deploy.ps1 --sync-env    update the server's .env (allowed keys only)
$bash = @("$env:ProgramFiles\Git\bin\bash.exe", "${env:ProgramFiles(x86)}\Git\bin\bash.exe") |
    Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $bash) { Write-Error "Git Bash not found; install Git for Windows."; exit 1 }
& $bash (Join-Path $PSScriptRoot "deploy.sh") @args
exit $LASTEXITCODE
