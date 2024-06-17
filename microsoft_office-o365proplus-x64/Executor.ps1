param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/office-o365proplus-x64"
$isolate = "merge-user"
$extra = "--enable=disablefontpreload"

StandardTest -image $image -isolate $isolate -localLogsDir $localLogsDir -extra $extra