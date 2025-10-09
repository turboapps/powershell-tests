param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Set the classic right click context menu
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v Start_ShowClassicMode /t REG_DWORD /d 1 /f

$image = "jamsoftware/treesize-free"
$isolate = "merge-user"
$extra = "--mount=$env:LOCALAPPDATA\microsoft\windows\inetcache"
$using = "turbobuild/isolate-edge-wc"

StandardTest -image $image -isolate $isolate -extra $extra -using $using -localLogsDir $localLogsDir