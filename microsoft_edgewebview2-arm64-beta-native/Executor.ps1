param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath
. (Join-Path -Path $PSScriptRoot -ChildPath "..\!include\NativeTest.ps1")

# Native-app test: no build behind it. The latest Edge Beta (which carries the Beta
# WebView2 runtime; there is no standalone Beta runtime installer) and the new Outlook (a
# WebView2 app; microsoft_outlook's installer and sikulix test) are installed natively,
# and Outlook is launched in a base container; no image is pulled.
$image = "microsoft/edgewebview2-arm64-beta-native"

PrepareTest -image $image -localLogsDir $localLogsDir -extra $extra

Invoke-NativeSetup -image $image -localLogsDir $localLogsDir -Setup {
    Remove-EdgeUpdateBlock
    Install-NativeEdge -Channel Beta -Architecture arm64 | Out-Null
    Set-NativeWebView2BetaPolicies
    $script:exe = Install-NativeOutlook -Architecture arm64
}

Start-NativeApp -image $image -exe $script:exe -extra $extra
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult
