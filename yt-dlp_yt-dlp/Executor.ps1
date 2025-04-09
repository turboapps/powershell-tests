param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "yt-dlp/yt-dlp"
$extra = $extra + " --startup-file=cmd "

StandardTest -image $image -extra $extra -shouldInstall $False -localLogsDir $localLogsDir