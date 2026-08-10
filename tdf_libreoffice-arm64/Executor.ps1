param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "tdf/libreoffice-arm64"
$using = "eclipse/temurinjre-lts-arm64,turbobuild/isolate-edge-wc"
$isolate = "merge-user"
$extra = "--enable=disablefontpreload"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir