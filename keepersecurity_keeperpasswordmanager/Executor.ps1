﻿param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "keepersecurity/keeperpasswordmanager"
$using = "turbobuild/isolate-edge-wc"

StandardTest -image $image -using $using -localLogsDir $localLogsDir