# The directory to store logs.
param (
        [string]$localLogsDir        
    )

# Import test related functions.
$CommonPath = Join-Path -Path $PSScriptRoot -ChildPath "..\Common\Test.ps1"
. $CommonPath

# Image to be used for testing.
$image = "adobe/acrobatpro"

# Dependencies of the image (`--using=`).
$using = "adobe/creativeclouddesktop,microsoft/office-o365proplus-x64,turbobuild/isolate-edge-wc"

# Isolation setting of `turbo run` and `turbo installi`.
$isolate = "merge-user"

# Extra parameters of `turbo run` and `turbo installi`.
$extra = "--enable=disablefontpreload"

# Run the standard app tests.
StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir