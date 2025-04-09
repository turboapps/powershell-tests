param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "jgm/pandoc"
$isolate = "merge-user"
$using = "tdf/libreoffice"


StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir -shouldTry $false