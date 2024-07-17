param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "rstudio/rstudio"
$using = "r-project/r,r-project/rtools"

StandardTest -image $image -using $using -extra $extra -localLogsDir $localLogsDir