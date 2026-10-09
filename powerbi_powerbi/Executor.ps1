param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "powerbi/powerbi"
$using = "turbobuild/isolate-edge-wc,microsoft/edgewebview2:155.0.4283.45"
$isolate = "merge-user"


StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir