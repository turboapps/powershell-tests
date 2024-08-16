param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/dotnet-desktop-runtime"
$app = "microsoft/dotnet-aspnet-runtime"
$using = "microsoft/dotnet-desktop-runtime,turbobuild/isolate-edge-wc"
$isolate = "merge-user"
$extra = "--startup-file=" + $PSScriptRoot + "\resources\MyAspNetCoreApp-x86\MyAspNetCoreApp.exe " + $extra

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $app -using $using
TryTurboApp -image $app -using $using -isolate $isolate -extra $extra -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult