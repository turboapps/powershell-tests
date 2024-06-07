param ([string]$LocalLogsDir)
$CommonPath = Join-Path -Path $PSScriptRoot -ChildPath "..\Common\Test.ps1"
. $CommonPath

$image = "npp/notepadplusplus"
$using = "turbobuild/isolate-edge-wc"
$isolate = "merge-user"

StandardTest -LocalLogsDir $LocalLogsDir -image $image -using $using -isolate $isolate 