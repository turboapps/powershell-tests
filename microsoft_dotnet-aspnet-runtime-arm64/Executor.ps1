param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/dotnet-aspnet-runtime-arm64"
$using = "microsoft/dotnet-desktop-runtime-arm64,turbobuild/isolate-edge-wc"
$isolate = "merge-user"
$extra = $extra + " --startup-file=" + $PSScriptRoot + "\resources\MyAspNetCoreApp-arm64\HelloWorldAspNet.exe "

StandardTest -image $image -using $using -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir