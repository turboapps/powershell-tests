param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "microsoft/edgewebview2"
$app = "powerbi/powerbi"
$using = "turbobuild/isolate-edge-wc,microsoft/edgewebview2:155.0.4283.45"
$isolate = "merge-user"

# PROBE ONLY - DO NOT MERGE: does --disable-gpu-sandbox let WebView2 155 start under the VM?
# turbo try takes --env (installi does not), so only the try launch carries it.
$tryExtra = ("$extra " + "--env=WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--disable-gpu-sandbox").Trim()
PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $app -using $using
InstallTurboApp -image $app -using $using -isolate $isolate -extra $extra
TryTurboApp -image $app -using $using -isolate $isolate -extra $tryExtra -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult