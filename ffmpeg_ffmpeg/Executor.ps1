param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "ffmpeg/ffmpeg"
$isolate = "merge-user"
$extra = $extra + " --startup-file=cmd "

StandardTest -image $image -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir