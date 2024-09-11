param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "autodesk/dwgtrueview"
$using = "turbobuild/isolate-edge-wc"
$isolate = "merge-user"
$extra = "--enable=disablefontpreload " + $extra

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir