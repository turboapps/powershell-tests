param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Disable the firewall to prevent the prompt
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

$image = "zoomvideocommunications/zoom-x64"
$using = "turbobuild/isolate-edge-wc"
$isolate = "merge-user"


StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir