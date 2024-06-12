param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "keepersecurity/keeperpasswordmanager-x64"
$using = "turbobuild/isolate-edge-wc"

StandardTest -image $image -using $using -localLogsDir $localLogsDir