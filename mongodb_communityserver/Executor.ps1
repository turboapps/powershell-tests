param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "mongodb/communityserver"
$app = "mongodb/compass"
$extra = "-n=mongodbserver"

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $app
PullTurboImages -image $image
InstallTurboApp -image $app
TryTurboApp -image $image -extra $extra -detached $True
TryTurboApp -image $app -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult