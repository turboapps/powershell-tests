param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "adobe/premierepro"
$using = "adobe/creativeclouddesktop,turbobuild/isolate-edge-wc"
$isolate = "merge-user"
$extra = "--enable=disablefontpreload " + $extra

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir