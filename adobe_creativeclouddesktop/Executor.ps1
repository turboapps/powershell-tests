param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "adobe/creativeclouddesktop"
$launch = "adobe/photoshop"
$using = "adobe/creativeclouddesktop,turbobuild/isolate-edge-wc"
$isolate = "merge-user"

StandardTest -image $launch -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir -shouldTry $false