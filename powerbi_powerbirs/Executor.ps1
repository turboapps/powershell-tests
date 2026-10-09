param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "powerbi/powerbirs"
$using = "turbobuild/isolate-edge-wc,microsoft/edgewebview2:155.0.4283.45"
$isolate = "merge-user"


# PROBE ONLY - DO NOT MERGE: does --disable-gpu-sandbox let WebView2 155 start under the VM?
# turbo try takes --env (installi does not), so only the try launch carries it.
$tryExtra = ("$extra " + "--env=WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--disable-gpu-sandbox").Trim()
PrepareTest -image $image -localLogsDir $localLogsDir -extra $extra
PullTurboImages -image $image -using $using
InstallTurboApp -image $image -using $using -isolate $isolate -extra $extra
TryTurboApp -image $image -using $using -isolate $isolate -extra $tryExtra -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir
exit $TestResult