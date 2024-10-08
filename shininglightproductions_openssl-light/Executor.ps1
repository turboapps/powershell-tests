param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "shininglightproductions/openssl-light"
$isolate = "merge-user"

StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir