param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "filezilla/filezillaserver-x64"
$isolate = "merge-user"


# Create a firewall rule to prevent the prompt
New-NetFirewallRule -DisplayName "Allow FileZilla Server" -Direction Inbound -Protocol TCP -LocalPort 21 -Action Allow -Profile Any

RunProcess -path "cmd.exe"
StandardTest -image $image -isolate $isolate -extra $extra -localLogsDir $localLogsDir