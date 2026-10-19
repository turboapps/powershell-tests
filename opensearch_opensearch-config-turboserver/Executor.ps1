param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "opensearch/opensearch-config-turboserver"
$app = "opensearch/opensearch"
$using = "opensearch/opensearch-config-turboserver"
$isolate = "merge-user"

New-Item -Path "C:\opensearch" -ItemType Directory
New-Item -Path "C:\opensearch\snapshots" -ItemType Directory

PrepareTest -image $image -localLogsDir $localLogsDir -extra $extra
PullTurboImages -image $app -using $using
# test.py launches Edge with `turbo try base --using=isolate-edge-wc`. Pull that
# layer here: a launch the Sikuli test issues does not inherit the executor's
# hub sign-in (TURBO_ACCESS_TOKEN on 26.10 clients), so an image it has to look
# up at the hub gets a 403 and the container exits at once ("Please login").
# On client 26.10.1552 Edge never opened and green-open.png failed 5/5.
PullTurboImage -image "turbobuild/isolate-edge-wc"
TryTurboApp -image $app -using $using -isolate $isolate -extra $extra -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult