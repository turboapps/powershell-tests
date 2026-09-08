param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "cerulean/trillian"

# -extra reaches the installi/try launches here and, via extra.txt, the second
# `turbo try` the test types into a Command Prompt (util.read_extra()).
StandardTest -image $image -extra $extra -localLogsDir $localLogsDir