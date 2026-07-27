param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "7-zip/7-zip-arm64"
$isolate = "merge-user"

StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir