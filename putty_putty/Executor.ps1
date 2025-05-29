param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Create firewall rules to prvent prompt
New-NetFirewallRule -DisplayName "Allow telnet" -Direction Inbound -Protocol TCP -LocalPort 23 -Action Allow -Profile Any
New-NetFirewallRule -DisplayName "Allow telnet" -Direction Inbound -Protocol UDP -LocalPort 23 -Action Allow -Profile Any

$image = "putty/putty"

StandardTest -image $image -extra $extra -localLogsDir $localLogsDir