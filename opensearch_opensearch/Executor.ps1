param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "opensearch/opensearch"
$using = "opensearch/opensearch-config-turboserver"
$isolate = "merge-user"

New-Item -Path "C:\opensearch" -ItemType Directory
New-Item -Path "C:\opensearch\snapshots" -ItemType Directory

StandardTest -image $image -using $using -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir