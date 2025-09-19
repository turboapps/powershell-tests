param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "apple/itunes-x64"
$isolate = "merge-user"

# Disable the firewall to prevent the prompt
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir
