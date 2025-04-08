param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Disable location awareness prompts to prevent a prompt during the test
reg add "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location" /v ShowGlobalPrompts /t REG_DWORD /d 0 /f

# Remove the MSIX MSTeams app that comes as part of Windows 11
Get-AppxPackage -AllUsers -Name "MSTeams" | Remove-AppxPackage -AllUsers

$image = "microsoft/teams"
$isolate = "merge-user"


StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir