param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/edgewebview2"
$app = "powerbi/powerbi"
$using = "turbobuild/isolate-edge-wc,microsoft/edgewebview2"
$isolate = "merge-user"

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $app -using $using
InstallTurboApp -image $app -using $using -isolate $isolate
TryTurboApp -image $app -using $using -isolate $isolate -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult