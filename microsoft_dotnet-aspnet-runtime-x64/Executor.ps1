﻿param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/dotnet-aspnet-runtime-x64"
$using = "microsoft/dotnet-desktop-runtime-x64,turbobuild/isolate-edge-wc"
$isolate = "merge-user"
$extra = "--startup-file=" + $PSScriptRoot + "\resources\MyAspNetCoreApp-x64\MyAspNetCoreApp.exe"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir