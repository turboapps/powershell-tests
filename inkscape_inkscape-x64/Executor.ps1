﻿param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "inkscape/inkscape-x64"
$using = "turbobuild/isolate-edge-wc"
$isolate = "merge-user"
$extra = "--enable=disablefontpreload,usedllinjection" + $extra

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir