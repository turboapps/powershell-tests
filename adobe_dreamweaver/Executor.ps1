param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "adobe/dreamweaver"
$using = "adobe/creativeclouddesktop,turbobuild/isolate-edge-wc"
$isolate = "merge-user"


New-Item -Path "$env:USERPROFILE\Desktop\test" -ItemType Directory

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir