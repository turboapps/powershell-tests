param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "pgvector/pgvector"

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $image
RunProcess -path (Join-Path -Path $PSScriptRoot -ChildPath "resources\setup.bat")
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult