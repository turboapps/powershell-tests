﻿param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "apache/tika"
$using = "eclipse/temurinjre-lts"

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $image -using $using
InstallTurboApp -image $image -using $using
TryTurboApp -image $image -using $using -extra "--startup-file=cmd $extra" -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

return $TestResult