param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath
. (Join-Path -Path $PSScriptRoot -ChildPath "..\!include\NativeTest.ps1")

# Native-app test: no build behind it. The latest WebView2 runtime and Power BI Desktop
# (the WebView2 host app microsoft_edgewebview2 drives) are installed natively, and Power
# BI is launched in a base container; no image is pulled.
# Power BI Desktop is x64-only: on this ARM64 VM it runs under x64 emulation against the
# ARM64 WebView2 runtime.
$image = "microsoft/edgewebview2-arm64-native"

PrepareTest -image $image -localLogsDir $localLogsDir -extra $extra

Invoke-NativeSetup -image $image -localLogsDir $localLogsDir -Setup {
    Remove-EdgeUpdateBlock
    Install-NativeWebView2
    $script:exe = Install-NativePowerBI
}

Start-NativeApp -image $image -exe $script:exe -extra $extra
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult
