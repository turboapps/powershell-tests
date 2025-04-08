param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "mongodb/compass"
$app = "mongodb/communityserver"

PrepareTest -image $image -localLogsDir $localLogsDir

# Run MongoDB to test MongoDB Compass.
PullTurboImages -image $image -using $app
InstallTurboApp -image $image -extra $extra
RunTurboApp -image $app -extra "$extra -n=mongodbserver" -detached $True

TryTurboApp -image $image -extra $extra -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

return $TestResult