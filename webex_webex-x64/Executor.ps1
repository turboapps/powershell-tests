param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "webex/webex-x64"
$isolate = "merge-user"

StandardTest -image $image -isolate $isolate -localLogsDir $localLogsDir