﻿param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "filezilla/filezilla-x64"
$using = "turbobuild/isolate-edge-wc"
$isolate = "merge-user"


StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir