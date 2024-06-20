param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "opensearch/opensearch-config-turboserver"
$app = "opensearch/opensearch"
$using = "opensearch/opensearch-config-turboserver"
$isolate = "merge-user"

New-Item -Path "C:\opensearch" -ItemType Directory
New-Item -Path "C:\opensearch\snapshots" -ItemType Directory

PrepareTest -image $image -localLogsDir $localLogsDir 
PullTurboImages -image $app -using $using
TryTurboApp -image $app -using $using -isolate $isolate  -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir 

exit $TestResult