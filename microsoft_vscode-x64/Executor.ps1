param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Disable the firewall to prevent the prompt
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

$image = "microsoft/vscode-x64"
$using = "python/python-x64,eclipse/temurin-lts,microsoft/dotnet-sdk-x64:8,turbobuild/isolate-edge-wc"
$isolate = "merge-user"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir
