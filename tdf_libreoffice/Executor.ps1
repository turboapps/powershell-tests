﻿param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "tdf/libreoffice"
$using = "eclipse/temurinjre-lts,turbobuild/isolate-edge-wc"
$isolate = "merge-user"
$extra = "--enable=disablefontpreload"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir