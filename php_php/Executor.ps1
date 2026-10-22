param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Create firewall rules to prevent the prompt
New-NetFirewallRule -DisplayName "Allow php" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Any
New-NetFirewallRule -DisplayName "Allow php" -Direction Inbound -Protocol UDP -LocalPort 8000 -Action Allow -Profile Any

# test.py launches the container itself rather than StandardTest's TryTurboApp. TryTurboApp adds
# --network=test, which puts the php server on a virtual network the native browser cannot reach
# at localhost:8000; test.py's launch leaves --network off so the server binds on the host.
$image = "php/php"

StandardTest -image $image -extra $extra -shouldInstall $False -shouldTry $False -localLogsDir $localLogsDir
