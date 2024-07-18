param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "putty/putty"

StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir