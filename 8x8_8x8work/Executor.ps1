﻿param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "8x8/8x8work"
$using = "turbobuild/isolate-edge-wc"

StandardTest -image $image -using $using -localLogsDir $localLogsDir