param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "cerulean/trillian"

StandardTest -image $image -using $using -localLogsDir $localLogsDir