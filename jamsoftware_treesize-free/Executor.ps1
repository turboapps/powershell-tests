param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "jamsoftware/treesize-free"
$isolate = "merge-user"
$extra = "--mount=$env:LOCALAPPDATA\microsoft\windows\inetcache"

StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir