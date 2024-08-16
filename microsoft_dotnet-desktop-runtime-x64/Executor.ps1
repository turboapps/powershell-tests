param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/dotnet-desktop-runtime-x64"
$app = "microsoft/dotnet-aspnet-runtime-x64"
$using = "microsoft/dotnet-desktop-runtime-x64,turbobuild/isolate-edge-wc"
$isolate = "merge-user"
$extra = "--startup-file=" + $PSScriptRoot + "\resources\MyAspNetCoreApp-x64\MyAspNetCoreApp.exe " + $extra

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $app -using $using
TryTurboApp -image $app -using $using -isolate $isolate -extra $extra -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult