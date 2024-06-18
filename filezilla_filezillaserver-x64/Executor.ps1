param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "filezilla/filezillaserver-x64"
$isolate = "merge-user"

RunProcess -path "cmd.exe"

StandardTest -image $image -isolate $isolate -localLogsDir $localLogsDir