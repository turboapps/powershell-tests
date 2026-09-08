param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "ffmpeg/ffmpeg"

# The test launches `turbo try` itself (test.py), so -extra reaches it through
# extra.txt (written by PrepareTest, read with util.read_extra()).
PrepareTest -image $image -localLogsDir $localLogsDir -extra $extra
PullTurboImages -image $image
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir