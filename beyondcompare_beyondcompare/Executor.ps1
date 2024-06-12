param (
        [string]$localLogsDir        
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "beyondcompare/beyondcompare"

StandardTest -image $image -localLogsDir $localLogsDir