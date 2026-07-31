param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Disable the firewall to prevent the prompt
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

$image = "apache/apache-x64"
$extra = $extra + ' -- -C "Listen 8080" -C "ServerName localhost:8080" -X -e debug '

StandardTest -image $image -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir