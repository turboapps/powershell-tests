param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Remove native vcredist if installed
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall' |
    ForEach-Object { Get-ItemProperty $_.PSPath } |
    Where-Object { $_.DisplayName -like '*Microsoft Visual C++*Arm64 Runtime*' } |
    ForEach-Object {
        $guid = [regex]::Match($_.UninstallString, '\{[0-9A-Fa-f-]{36}\}').Value
        Start-Process msiexec.exe -ArgumentList "/x $guid /qn /passive /norestart" -Wait
    }

$image = "microsoft/vcredist-arm64"
$extra = $extra + " --startup-file=" + $PSScriptRoot + "\resources\vcredisttest.exe "

StandardTest -image $image -extra $extra -shouldInstall $False -localLogsDir $localLogsDir