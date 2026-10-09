param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "bluebeam/revu"
$using = "turbobuild/isolate-edge-wc,microsoft/edgewebview2:154.0.4258.62"
$isolate = "merge-user"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir