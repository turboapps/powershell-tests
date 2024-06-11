param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "python/python"
$extra = "--startup-file=cmd"

StandardTest -image $image -extra $extra -localLogsDir $localLogsDir