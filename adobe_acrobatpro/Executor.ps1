# The extra parameters for `turbo run` and `turbo installi` and the directory to store logs.
param (
        [string]$extra,
        [string]$localLogsDir
    )

# Import test related functions.
$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Image to be used for testing.
$image = "adobe/acrobatpro"

# Dependencies of the image (`--using=`).
$using = "adobe/creativeclouddesktop,microsoft/office-o365proplus-x64,turbobuild/isolate-edge-wc"

# Isolation setting of `turbo run` and `turbo installi`.
$isolate = "merge-user"

# Extra parameters of `turbo run` and `turbo installi`.


# Run the standard app tests.
StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir -shouldTry $false