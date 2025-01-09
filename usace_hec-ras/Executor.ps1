param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$resources = Join-Path -Path $PSScriptRoot -ChildPath "resources"
Copy-Item -Path (Join-Path -Path $resources -ChildPath "HEC Data") -Destination (Join-Path -Path ([Environment]::GetFolderPath("MyDocuments")) -ChildPath "HEC Data") -Recurse -Force


$image = "usace/hec-ras"
$isolate = "merge-user"

StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir