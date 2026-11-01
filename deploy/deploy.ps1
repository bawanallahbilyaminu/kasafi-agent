# PowerShell wrapper for deploy/deploy.sh: runs it with Git Bash in THIS window (no new window that closes),
# with the same flags, and returns its exit code. Needs Git for Windows; nothing else to install.
#   .\deploy\deploy.ps1                   deploy the pushed main
#   .\deploy\deploy.ps1 --rollback        go back one release
#   .\deploy\deploy.ps1 --sync-env        update the server's .env (allowed keys only)
#   .\deploy\deploy.ps1 --sync-index      copy the document index from the dev database
#   .\deploy\deploy.ps1 --sync-pdfs       copy new or changed source PDFs
#   .\deploy\deploy.ps1 --help            every mode
# The full output of each run is also in deploy\logs\.

# Git's own bash.exe (bin\, not git-bash.exe, which opens a separate window; not WSL's System32\bash.exe)
$candidates = @()
$git = Get-Command git -ErrorAction SilentlyContinue
if ($git) { $candidates += (Join-Path (Split-Path (Split-Path $git.Source)) "bin\bash.exe") }
$candidates += "$env:ProgramFiles\Git\bin\bash.exe", "${env:ProgramFiles(x86)}\Git\bin\bash.exe",
               "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe"
$bash = $candidates | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
if (-not $bash) { Write-Error "Git Bash not found; install Git for Windows."; exit 1 }

# UTF-8 so the progress bars, the spinner and the ✓ / ✗ lines draw correctly
$prev = [Console]::OutputEncoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$repo = Split-Path $PSScriptRoot -Parent
Push-Location $repo
try {
    & $bash "deploy/deploy.sh" @args
    $code = $LASTEXITCODE
} finally {
    Pop-Location
    [Console]::OutputEncoding = $prev
}
exit $code
