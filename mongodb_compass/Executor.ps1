param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "mongodb/compass"
$extra = "-n=mongodbserver"

PullTurboImages -image "mongodb/communityserver"
TryTurboApp -image "mongodb/communityserver" -extra $extra -detached $True

StandardTest -image $image -using $using -extra $extra -localLogsDir $localLogsDir