param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$outputDir = [Environment]::GetFolderPath("Desktop")

$image = "turbo/headless-extractor"
$using = "google/chrome-x64"
$isolate = "merge-user"
$extra = $extra + " --startup-file=powershell -- C:\extractor\Extract.ps1 -OutputDir $outputDir -Url https://turbo.net -Screenshot -DOM -ExtractLinks "

StandardTest -image $image -using $using -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir
