param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Create firewall rules to prvent prompt
New-NetFirewallRule -DisplayName "Allow node" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow -Profile Any
New-NetFirewallRule -DisplayName "Allow node" -Direction Inbound -Protocol UDP -LocalPort 3000 -Action Allow -Profile Any

$image = "nodejs/nodejs-arm64"
$using = "python/python-arm64,microsoft/vsbuildtools"
# --startup-file=cmd: the image's default startup (cmd /k nodevars.bat) crashes at launch
# on the win11-arm pool (VM bug - cmd.exe faults in ntdll with 0xC00000FF when the startup
# file has commandLine args). Plain cmd works and node is on the container PATH regardless.
$extra = $extra + " --enable=usedllinjection --startup-file=cmd --working-dir=" + $PSScriptRoot + "\resources "

StandardTest -image $image -using $using -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir