param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath
. (Join-Path -Path $PSScriptRoot -ChildPath "..\!include\NativeTest.ps1")

# Native-app test: no build behind it. The latest Edge Stable is installed natively and
# launched in a base container; no Edge image is pulled.
$image = "microsoft/edge-arm64-native"
$userDataDir = "$env:USERPROFILE\Edge"

PrepareTest -image $image -localLogsDir $localLogsDir -extra $extra

Invoke-NativeSetup -image $image -localLogsDir $localLogsDir -Setup {
    Remove-EdgeUpdateBlock
    $script:exe = Install-NativeEdge -Channel Stable -Architecture arm64
    Set-NativeEdgePolicies
    Initialize-NativeEdgeProfile -Exe $script:exe -SetupSwitches "--msedge" -UserDataDir $userDataDir -LocalState "$PSScriptRoot\resources\Local State"
}

Start-NativeApp -image $image -exe $script:exe -appArgs "--user-data-dir=`"$userDataDir`"" -extra $extra
HidePowerShellWindow
$TestResult = StartTest -image $image -localLogsDir $localLogsDir

exit $TestResult
