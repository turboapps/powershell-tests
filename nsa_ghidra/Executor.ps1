param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Disable the firewall to prevent the prompt
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

$image = "nsa/ghidra"
$using = "eclipse/temurin"
$isolate = "merge-user"


New-Item -Path "$env:USERPROFILE\Desktop\ghidra-test" -ItemType Directory
New-Item -Path "$env:USERPROFILE\Desktop\ghidra-test-headless" -ItemType Directory

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir