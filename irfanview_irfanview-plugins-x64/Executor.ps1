param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "irfanview/irfanview-plugins-x64"
$app = "irfanview/irfanview-x64"
$using = "irfanview/irfanview-plugins-x64"
$isolate = "merge-user"

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $app -using $using
InstallTurboApp -image $app -using $using -isolate $isolate -extra $extra
TryTurboApp -image $app -using $using -isolate $isolate -extra $extra -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult