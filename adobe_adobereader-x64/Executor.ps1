﻿param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "adobe/adobereader-x64"
$using = "turbobuild/isolate-edge-wc"
$isolate = "merge-user"

StandardTest -image $image -using $using -isolate $isolate -localLogsDir $localLogsDir