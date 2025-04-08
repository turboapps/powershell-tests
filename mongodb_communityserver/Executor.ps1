param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "mongodb/communityserver"
$app = "mongodb/compass"

PrepareTest -image $image -localLogsDir $localLogsDir

# Run MongoDB to test MongoDB Compass.
PullTurboImages -image $image -using $app
InstallTurboApp -image $app -extra $extra
RunTurboApp -image $image -extra "$extra -n=mongodbserver" -detached $True

TryTurboApp -image $app -extra $extra -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

return $TestResult