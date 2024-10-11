param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "git/git"
$using = "turbobuild/isolate-edge-wc"
$isolate = "merge+merge-user"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir