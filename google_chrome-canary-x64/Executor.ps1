param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "google/chrome-canary-x64"
$isolate = "merge-user"
# $extra = "-- --no-sandbox"  # only use this for testing

StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir