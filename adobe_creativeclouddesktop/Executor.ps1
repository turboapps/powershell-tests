param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "adobe/creativeclouddesktop"
# Creative Cloud Desktop is exercised through Photoshop: -app launches
# Photoshop, while -image keeps the test (test.sikuli, secrets.txt and the
# <app>-test.log CI reads back) on adobe_creativeclouddesktop.
$launch = "adobe/photoshop"
$using = "adobe/creativeclouddesktop,turbobuild/isolate-edge-wc"
$isolate = "merge-user"

StandardTest -image $image -app $launch -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir -shouldTry $false