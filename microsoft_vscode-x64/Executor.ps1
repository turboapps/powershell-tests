param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Disable the firewall to prevent the prompt
Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled False

# Clean up files from previous test run
$paths = @(
    "$env:USERPROFILE\Desktop\hello_world.py",
    "$env:USERPROFILE\.vscode",
    "$env:USERPROFILE\.vscode-shared"
    "$env:USERPROFILE\.dotnet"
)

foreach ($path in $paths) {
    if (Test-Path $path) {
        Remove-Item $path -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "Deleted: $path"
    } else {
        Write-Host "Not found: $path"
    }
}

$image = "microsoft/vscode-x64"
$using = "python/python-x64,eclipse/temurin-lts,microsoft/dotnet-sdk-x64:8,turbobuild/isolate-edge-wc"
$isolate = "merge-user"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir
