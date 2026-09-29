param (
        [string]$extra,
        [string]$localLogsDir
    )

# REPRO BRANCH - do not merge. Runs Repro-SignInBlankHost.ps1 in place of the sikuli test and
# reports its verdict through the test log the CI harness reads: an [error] line = reproduced.

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "adobe/adobereader"
if ([string]::IsNullOrWhiteSpace($localLogsDir)) { $localLogsDir = "$env:USERPROFILE\Desktop" }
PrepareTest -image $image -localLogsDir $localLogsDir -extra $extra   # hub login, clean turbo state
HidePowerShellWindow

$vm = if ($extra -match '--vm=(\S+)') { $Matches[1] } else { '' }
$out = "$localLogsDir\adobe_adobereader-vm-logs"
& "$PSScriptRoot\Repro-SignInBlankHost.ps1" -Xvm $vm -MaxIterations 3 -OutRoot $out
$rc = $global:LASTEXITCODE

$log = "$localLogsDir\adobe_adobereader-test.log"
$lines = @(Get-Content "$out\repro.log" -ErrorAction SilentlyContinue)
$lines | Where-Object { $_ -match 'clicking|: RdrCEF|missed' } | ForEach-Object { "[info] $_" } | Set-Content $log
switch ($rc) {
    1 { Add-Content $log "[error] REPRODUCED: RdrCEF.exe exited 0x80000003 after Sign in (see adobe_adobereader-vm-logs)" }
    0 { Add-Content $log "[info] not reproduced in 3 iterations" }
    default { Add-Content $log "[error] repro script failed (exit $rc): $($lines | Where-Object { $_ -match 'ERROR' } | Select-Object -Last 1)" }
}
Write-Host "Repro verdict: exit $rc"
Get-Content $log | Write-Host
exit $rc
