﻿param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "eclipse/temurin"

StandardTest -image $image -extra $extra -localLogsDir $localLogsDir