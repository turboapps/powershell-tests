param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/azuredatastudio"
$using = "turbobuild/isolate-edge-wc"
$isolate = "merge-user"


# Create a firewall rule to prevent the prompt
New-NetFirewallRule -DisplayName "Allow SQL Server" -Direction Inbound -Protocol TCP -LocalPort 1433 -Action Allow -Profile Any
New-NetFirewallRule -DisplayName "Allow SQL Server" -Direction Inbound -Protocol UDP -LocalPort 1433 -Action Allow -Profile Any

PrepareTest -image $image -localLogsDir $localLogsDir

# Run SQL Server Express to test Azure Data Studio.
PullTurboImages -image "sqlserver/sqlserver-express" -using "microsoft/dotnet" -isolate "merge-user"
RunTurboApp -image "sqlserver/sqlserver-express" -using "microsoft/dotnet" -isolate "merge-user" -extra $extra -detached $True

PullTurboImages -image $image -using $using
InstallTurboApp -image $image -using $using -isolate $isolate -extra $extra
TryTurboApp -image $image -using $using -isolate $isolate -extra $extra -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

# Stop the session of SQL Server Express.
RunProcess -path "turbo.exe" -arguments "stop sqlserver-express" -shouldWait $True

return $TestResult