param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "telerik/fiddlerclassic"
$using = "turbobuild/isolate-edge-wc"

StandardTest -image $image -using $using -extra $extra -localLogsDir $localLogsDir