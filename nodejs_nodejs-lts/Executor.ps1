param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "nodejs/nodejs-lts"
$using = "python/python-x64,microsoft/vsbuildtools"
$extra = "--working-dir=" + $PSScriptRoot + "\resources " + $extra

StandardTest -image $image -using $using -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir