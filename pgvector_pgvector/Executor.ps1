param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "pgvector/pgvector"
$using = "postgresql/postgresql:16"

# Save the extra parameters to a TXT file that can be read by the test script.
Set-Content -Path (Join-Path -Path $PSScriptRoot -ChildPath "extra.txt") -Value $extra

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $image
PullTurboImages -image $using
RunProcess -path (Join-Path -Path $PSScriptRoot -ChildPath "resources\setup.bat")
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult