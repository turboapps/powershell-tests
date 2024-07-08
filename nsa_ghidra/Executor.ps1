param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "nsa/ghidra"
$using = "eclipse/temurin"
$isolate = "merge-user"

New-Item -Path "$env:USERPROFILE\Desktop\ghidra-test" -ItemType Directory
New-Item -Path "$env:USERPROFILE\Desktop\ghidra-test-headless" -ItemType Directory

StandardTest -image $image -using $using -isolate $isolate -localLogsDir $localLogsDir