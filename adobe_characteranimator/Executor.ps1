param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "adobe/characteranimator"
$using = "adobe/creativeclouddesktop,turbobuild/isolate-edge-wc"
$isolate = "merge-user"

Copy-Item -Path "$PSScriptRoot\resources\opencl.dll" -Destination "C:\Windows\System32" -Force
& regsvr32 /s "C:\Windows\System32\opencl.dll"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir -shouldTry $false