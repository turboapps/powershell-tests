﻿param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "eclipse/temurinjre-lts"

StandardTest -image $image -extra $extra -localLogsDir $localLogsDir