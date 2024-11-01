param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "adobe/aftereffects"
$using = "adobe/creativeclouddesktop,turbobuild/isolate-edge-wc,microsoft/vcredist"
$isolate = "merge-user"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir -shouldTry $false