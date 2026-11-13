param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "postgresql/postgresql"

# Save the extra parameters to a TXT file that can be read by the test script.
Set-Content -Path (Join-Path -Path $PSScriptRoot -ChildPath "extra.txt") -Value $extra

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $image
# The test's console runs as another user (postgres) and launches postgresql:16 with pgvector.
# Turbo Client 26.10 shares one image repository across the machine that only an administrator
# may download into, so pull both here, as the harness's user (as pgvector_pgvector does).
PullTurboImages -image "postgresql/postgresql:16" -using "pgvector/pgvector"
HidePowerShellWindow
$setupfile = Join-Path -Path $PSScriptRoot -ChildPath "resources\setup.bat"
Start-Process -FilePath "cmd.exe" -ArgumentList "/c `"$setupfile`""
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult