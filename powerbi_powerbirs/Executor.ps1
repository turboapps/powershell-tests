param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "powerbi/powerbirs"
$using = "turbobuild/isolate-edge-wc,microsoft/edgewebview2"
$isolate = "merge-user"

StandardTest -image $image -using $using -isolate $isolate -localLogsDir $localLogsDir