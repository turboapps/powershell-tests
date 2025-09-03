param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Disable the firewall to prevent the prompt
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

$image = "adobe/dreamweaver"
$using = "adobe/creativeclouddesktop,turbobuild/isolate-edge-wc"
$isolate = "merge-user"


New-Item -Path "$env:USERPROFILE\Desktop\test" -ItemType Directory

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir -shouldTry $false