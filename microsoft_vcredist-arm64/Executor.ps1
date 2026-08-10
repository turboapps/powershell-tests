param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/vcredist-arm64"
$extra = $extra + " --startup-file=" + $PSScriptRoot + "\resources\vcredisttest.exe "

StandardTest -image $image -extra $extra -shouldInstall $False -localLogsDir $localLogsDir