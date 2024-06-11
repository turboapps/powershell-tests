# The directory to store logs.
param (
        [string]$localLogsDir        
    )

# Import test related functions.
$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Image to be used for testing.
$image = "7-zip/7-zip"

# Isolation setting of `turbo run` and `turbo installi`.
$isolate = "merge-user"

# Run the standard app tests.
StandardTest -image $image -isolate $isolate -localLogsDir $localLogsDir