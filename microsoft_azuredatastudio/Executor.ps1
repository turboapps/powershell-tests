﻿param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/azuredatastudio"
$using = "turbobuild/isolate-edge-wc"
$isolate = "merge-user"

PrepareTest -image $image -localLogsDir $localLogsDir

# Run SQL Server Express to test Azure Data Studio.
PullTurboImages -image "sqlserver/sqlserver-express" -using "microsoft/dotnet" -isolate "merge-user"
RunTurboApp -image "sqlserver/sqlserver-express" -using "microsoft/dotnet" -isolate "merge-user" -detached $True

PullTurboImages -image $image -using $using
InstallTurboApp -image $image -using $using -isolate $isolate
TryTurboApp -image $image -using $using -isolate $isolate -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

# Stop the session of SQL Server Express.
RunProcess -path "turbo.exe" -arguments "stop sqlserver-express" -shouldWait $True

return $TestResult