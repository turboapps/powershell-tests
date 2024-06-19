param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/vscode-x64"
$using = "turbobuild/isolate-edge-wc"
$isolate = "merge-user"

StandardTest -image $image -using $using -isolate $isolate -localLogsDir $localLogsDir