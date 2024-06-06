# The directory to store logs.
param (
        [string]$localLogsDir        
    )

# Import test related functions.
$CommonPath = Join-Path -Path $PSScriptRoot -ChildPath "..\Common\Test.ps1"
. $CommonPath

# Image to be used for testing.
$image = "7-zip/7-zip"

# Isolation setting of `turbo run` and `turbo installi`.
$isolate = "merge-user"

# Run the standard app tests.
StandardTest -image $image -isolate $isolate -localLogsDir $localLogsDir