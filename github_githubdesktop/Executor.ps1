param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

if (Test-Path "$env:USERPROFILE\.gitconfig") {
    Remove-Item "$env:USERPROFILE\.gitconfig" -Force -ErrorAction SilentlyContinue
}

$image = "github/githubdesktop"
$using = "turbobuild/isolate-edge-wc"
$isolate = "merge+merge-user"

StandardTest -image $image -using $using -isolate $isolate -extra $extra -localLogsDir $localLogsDir