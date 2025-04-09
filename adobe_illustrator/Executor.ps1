param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "adobe/illustrator"
$using = "adobe/creativeclouddesktop,microsoft/vcredist"
$isolate = "merge-user"


StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir