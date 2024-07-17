param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/vcredist"
$extra = "--startup-file=" + $PSScriptRoot + "\resources\vcredisttest.exe " + $extra

StandardTest -image $image -extra $extra -shouldInstall $False -localLogsDir $localLogsDir