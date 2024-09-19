param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "mongodb/compass"
$app = "mongodb/communityserver"
$extra = "-n=mongodbserver"

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $app
PullTurboImages -image $image
InstallTurboApp -image $image
TryTurboApp -image $app -extra $extra -detached $True
TryTurboApp -image $image -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult