param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/dotnet-runtime-x64"
$isolate = "merge-user"

StandardTest -image $image -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir