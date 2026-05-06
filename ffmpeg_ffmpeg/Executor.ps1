param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "ffmpeg/ffmpeg"

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $image
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir