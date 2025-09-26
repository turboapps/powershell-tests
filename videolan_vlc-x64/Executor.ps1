param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "videolan/vlc-x64"
$isolate = "merge-user"

$dropPath = Join-Path $PSScriptRoot "resources\drop.avi"
Copy-Item $dropPath "$env:USERPROFILE\Desktop\drop.avi" -Force

StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir