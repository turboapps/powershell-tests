param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "r-project/rtools"
$app = "rstudio/rstudio"
$using = "r-project/r,r-project/rtools"

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $app -using $using
InstallTurboApp -image $app -using $using -extra $extra
TryTurboApp -image $app -using $using -extra $extra -detached $True
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult