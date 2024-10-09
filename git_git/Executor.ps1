param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "git/git"
$isolate = "merge+merge-user"
$using = "turbobuild/isolate-edge-wc"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir