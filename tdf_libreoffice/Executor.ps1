param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "tdf/libreoffice"
$using = "eclipse/temurinjre-lts,turbobuild/isolate-edge-wc"
$extra = "--enable=disablefontpreload"
$isolate = "merge-user"

StandardTest -image $image -isolate $isolate -using $using -extra $extra -localLogsDir $localLogsDir