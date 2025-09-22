param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "videolan/vlc"
$isolate = "merge-user"

Copy-Item ".\resources\drop.avi" "$env:USERPROFILE\Desktop\drop.avi" -Force

StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir