﻿param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/winget"
$isolate = "merge"

RunProcess -path "cmd"
StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir