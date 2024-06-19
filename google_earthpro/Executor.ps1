param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "google/earthpro"
$using = "turbobuild/isolate-edge-wc"
$isolate = "write-copy+merge-user"
$extra = " -setDX"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir