<#
.SYNOPSIS
    Reproduce the DWG TrueView shutdown double free on a bare machine.

.DESCRIPTION
    dwgviewr.exe dies with c0000374 STATUS_HEAP_CORRUPTION - bucket
    HEAP_CORRUPTION_ACTIONABLE_BlockNotBusy_DOUBLE_FREE - when a SECOND window
    close arrives while it is already running its own shutdown. The stack is
    Autodesk's own:

        mfc140u!AfxWinMain -> accore!AcApAppImp::run -> accore!AcApApp::terminate
          -> acdb25!AcRxImpDynamicLinker::unloadAllModules -> ::unloadModuleEx
          -> acdbmgd!Terminate -> accoremgd!acrxEntryPoint -> coreclr!ThePreStub
          -> JIT'd managed code -> mfc140u!CStringT::~CStringT -> free

    and the block freed twice is always the same static MFC CString: pStringMgr
    mfc140u, nDataLength 4, nAllocLength 4, nRefs -1, data "acad".

    In CI the second close comes from `turbo stop`, whose entire payload - per the
    VM's own diagnostic log - is PostMessageW(WM_CLOSE) to every top-level window
    of the process (CSystemManager::TerminateSelfGracefullyCallback in
    vm/Vm/Engine/vm.cpp). isConsoleApp is 0 so its CTRL_CLOSE_EVENT does nothing,
    and the process dies long before its 10 s TerminateProcess timer.

    This script drives that directly. No SikuliX, no image matching, no runner:
    readiness is a real window plus a CPU-quiet check, and every close is a
    PostMessage, so nothing here depends on focus.

.PARAMETER Mode
    TurboStop       Close the main window, then `turbo stop`. Reproduces CI.
    TurboStopAfter  Close the main window, wait for the process to exit, THEN
                    `turbo stop`. Control arm - measured 0/27 in CI.
    Native          No container at all. Launch the installed dwgviewr.exe,
                    close its main window, then broadcast WM_CLOSE to every
                    top-level window exactly as _PostWmCloseIf does.
                    This is the arm that decides whether Turbo is needed to
                    provoke the bug or merely happens to be what provokes it.

.PARAMETER SecondCloseDelayMs
    Gap between the first close and the second. In CI the Alt+F4 -> `turbo stop`
    gap was 1.3 s and 2.3 s, and the crash followed ~4 s later. The app exits in
    about 2 s, so the window is narrow - sweep this if a mode will not reproduce.

.EXAMPLE
    .\Repro-DwgTrueViewDoubleFree.ps1 -Mode TurboStop -Iterations 10
    Expect roughly half the iterations to crash.

.EXAMPLE
    .\Repro-DwgTrueViewDoubleFree.ps1 -Mode Native -Iterations 10
    Crashes here => an Autodesk defect any WM_CLOSE broadcast can trigger.
    Clean here while TurboStop crashes => something about the container matters.

.EXAMPLE
    foreach ($d in 400,800,1200,1600,2000,2400) {
        .\Repro-DwgTrueViewDoubleFree.ps1 -Mode Native -Iterations 5 -SecondCloseDelayMs $d
    }
    Sweep for the timing window.

.NOTES
    Run elevated: WER LocalDumps lives under HKLM. The script saves whatever was
    there and puts it back on exit unless -KeepWerSettings is given.
#>
[CmdletBinding()]
param(
    [ValidateSet('TurboStop', 'TurboStopAfter', 'Native')]
    [string]$Mode = 'TurboStop',

    [int]$Iterations = 10,
    [int]$SecondCloseDelayMs = 1500,

    [string]$Image = 'autodesk/dwgtrueview',
    [string]$SessionName = 'dwgrepro',
    [string]$XvmVersion = '',

    [string]$DumpDir = 'C:\dwgrepro-dumps',
    [int]$ReadyTimeoutSec = 240,
    [int]$QuietSec = 8,
    [int]$PostCrashGraceSec = 20,

    [switch]$KeepWerSettings,
    [switch]$SkipDumpAnalysis
)

$ErrorActionPreference = 'Stop'
$ProcName = 'dwgviewr'
$ExeName  = 'dwgviewr.exe'

# ---------------------------------------------------------------------------
# Win32. Every close is a PostMessage rather than a synthesized Alt+F4: WM_CLOSE
# is what Alt+F4 turns into anyway, and posting it removes the focus dependency
# that makes UI automation of this flaky.
# ---------------------------------------------------------------------------
if (-not ('DwgRepro.Win32' -as [type])) {
    Add-Type -TypeDefinition @"
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

namespace DwgRepro {
    public class Win32 {
        public delegate bool EnumProc(IntPtr hWnd, IntPtr lParam);
        [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr lParam);
        [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint pid);
        [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern bool PostMessageW(IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam);
        [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr hWnd);
        [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowTextW(IntPtr hWnd, StringBuilder s, int max);
        [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowTextLengthW(IntPtr hWnd);

        public const uint WM_CLOSE = 0x0010;

        // Every top-level window owned by the process, in EnumWindows order -
        // the same enumeration _PostWmCloseIf walks.
        public static List<IntPtr> TopLevelWindows(uint pid) {
            List<IntPtr> found = new List<IntPtr>();
            EnumWindows(delegate(IntPtr h, IntPtr l) {
                uint owner; GetWindowThreadProcessId(h, out owner);
                if (owner == pid) found.Add(h);
                return true;
            }, IntPtr.Zero);
            return found;
        }

        public static string TitleOf(IntPtr hWnd) {
            int len = GetWindowTextLengthW(hWnd);
            if (len <= 0) return "";
            StringBuilder sb = new StringBuilder(len + 1);
            GetWindowTextW(hWnd, sb, sb.Capacity);
            return sb.ToString();
        }

        public static bool Visible(IntPtr hWnd) { return IsWindowVisible(hWnd); }
    }
}
"@
}

function Write-Step($msg) { Write-Host ("[{0:HH:mm:ss}] {1}" -f (Get-Date), $msg) }

# ---------------------------------------------------------------------------
# WER LocalDumps. Full dumps, into our own folder, so a dump in there was
# written by this run and nothing else. Mirrors the applab workflow's setup.
# ---------------------------------------------------------------------------
$WerKey = 'HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps'
$script:WerSaved = $null

function Enable-WerLocalDumps {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not (New-Object Security.Principal.WindowsPrincipal $id).IsInRole(
              [Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Run elevated: WER LocalDumps is under HKLM."
    }
    New-Item -ItemType Directory -Path $DumpDir -Force | Out-Null
    if (Test-Path $WerKey) {
        $script:WerSaved = Get-ItemProperty -Path $WerKey
    } else {
        New-Item -Path $WerKey -Force | Out-Null
    }
    New-ItemProperty -Path $WerKey -Name DumpFolder -Value $DumpDir -PropertyType ExpandString -Force | Out-Null
    New-ItemProperty -Path $WerKey -Name DumpType   -Value 2       -PropertyType DWord        -Force | Out-Null
    New-ItemProperty -Path $WerKey -Name DumpCount  -Value 20      -PropertyType DWord        -Force | Out-Null
    # No modal WER dialog: one would wedge an unattended run.
    New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting' `
        -Name DontShowUI -Value 1 -PropertyType DWord -Force | Out-Null
    Write-Step "WER LocalDumps -> $DumpDir (full dumps, keep 20)"
}

function Restore-WerLocalDumps {
    if ($KeepWerSettings) { Write-Step "Leaving WER settings in place (-KeepWerSettings)"; return }
    try {
        if ($null -eq $script:WerSaved) {
            Remove-Item -Path $WerKey -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            foreach ($n in 'DumpFolder', 'DumpType', 'DumpCount') {
                if ($null -ne $script:WerSaved.$n) {
                    Set-ItemProperty -Path $WerKey -Name $n -Value $script:WerSaved.$n
                } else {
                    Remove-ItemProperty -Path $WerKey -Name $n -ErrorAction SilentlyContinue
                }
            }
        }
        Write-Step "WER settings restored"
    } catch { Write-Warning "Could not restore WER settings: $_" }
}

# ---------------------------------------------------------------------------
# Launch / readiness
# ---------------------------------------------------------------------------
function Get-NativeExe {
    $hit = Get-ChildItem -Path 'C:\Program Files\Autodesk\DWG TrueView*\dwgviewr.exe' -ErrorAction SilentlyContinue |
           Select-Object -First 1
    if (-not $hit) { throw "No installed dwgviewr.exe under C:\Program Files\Autodesk\DWG TrueView*." }
    return $hit.FullName
}

function Start-App {
    if ($Mode -eq 'Native') {
        $exe = Get-NativeExe
        Write-Step "Launching $exe (no container)"
        Start-Process -FilePath $exe -ArgumentList '/language', 'en-US' | Out-Null
        return
    }
    # The launch the CI executor makes, verbatim except for the session name.
    $turboArgs = @(
        'try', $Image, "--name=$SessionName",
        '--enable=disablefontpreload,usedllinjection,cachefileinfo',
        '--network=test', '--disable-proxy-resolve-via-proxy',
        '--using=turbobuild/isolate-edge-wc', '--isolate=merge-user', '-d'
    )
    if ($XvmVersion) { $turboArgs += "--vm=$XvmVersion" }
    Write-Step "turbo $($turboArgs -join ' ')"
    Start-Process -FilePath 'turbo.exe' -ArgumentList $turboArgs -NoNewWindow -Wait | Out-Null
}

function Get-AppProcess {
    Get-Process -Name $ProcName -ErrorAction SilentlyContinue | Select-Object -First 1
}

# Ready = a visible, titled top-level window, and then CPU quiet for QuietSec.
#
# The Start tab keeps working for a while after the frame appears, and closing
# mid-load is not the state the CI failures were in - they closed a settled app.
# CPU-quiet stands in for "the Start tab finished" without matching any image.
function Wait-AppReady {
    $deadline = (Get-Date).AddSeconds($ReadyTimeoutSec)
    $proc = $null
    while ((Get-Date) -lt $deadline) {
        $proc = Get-AppProcess
        if ($proc) {
            $titled = @(Get-AppWindows -TargetPid $proc.Id | Where-Object { $_.Visible -and $_.Title })
            if ($titled.Count -gt 0) { break }
        }
        Start-Sleep -Milliseconds 500
    }
    if (-not $proc) { return $null }

    $last = $proc.TotalProcessorTime
    $quiet = 0
    while ((Get-Date) -lt $deadline -and $quiet -lt $QuietSec) {
        Start-Sleep -Seconds 1
        try { $proc.Refresh() } catch { return $null }
        if ($proc.HasExited) { return $null }
        $now = $proc.TotalProcessorTime
        # Under 50 ms of CPU in a second counts as idle.
        if (($now - $last).TotalMilliseconds -lt 50) { $quiet++ } else { $quiet = 0 }
        $last = $now
    }
    return (Get-AppProcess)
}

function Get-AppWindows {
    param([int]$TargetPid)
    foreach ($h in [DwgRepro.Win32]::TopLevelWindows([uint32]$TargetPid)) {
        [pscustomobject]@{
            Handle  = $h
            Title   = [DwgRepro.Win32]::TitleOf($h)
            Visible = [DwgRepro.Win32]::Visible($h)
        }
    }
}

# ---------------------------------------------------------------------------
# The two closes
# ---------------------------------------------------------------------------

# First close: what Alt+F4 does - WM_CLOSE to the app's visible main window.
function Close-MainWindow {
    param([int]$TargetPid)
    $main = @(Get-AppWindows -TargetPid $TargetPid | Where-Object { $_.Visible -and $_.Title }) | Select-Object -First 1
    if (-not $main) { Write-Warning "No visible main window for pid $TargetPid"; return $false }
    Write-Step ("  close #1 -> `"{0}`"" -f $main.Title)
    [void][DwgRepro.Win32]::PostMessageW($main.Handle, [DwgRepro.Win32]::WM_CLOSE, [IntPtr]::Zero, [IntPtr]::Zero)
    return $true
}

# Second close: _PostWmCloseIf, reimplemented. Every top-level window of the
# process, no visibility filter, no check for whether it is already exiting -
# that lack of a check is the whole point.
function Send-WmCloseBroadcast {
    param([int]$TargetPid)
    $windows = @(Get-AppWindows -TargetPid $TargetPid)
    $n = 0
    foreach ($w in $windows) {
        if ([DwgRepro.Win32]::PostMessageW($w.Handle, [DwgRepro.Win32]::WM_CLOSE, [IntPtr]::Zero, [IntPtr]::Zero)) { $n++ }
    }
    Write-Step "  close #2 -> WM_CLOSE broadcast to $n top-level window(s)"
    return $n
}

function Stop-TurboSession {
    Start-Process -FilePath 'turbo.exe' -ArgumentList @('stop', $SessionName) -NoNewWindow -Wait | Out-Null
}

function Wait-ProcessGone {
    param([int]$TimeoutSec = 120)
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    $t0 = Get-Date
    while ((Get-Date) -lt $deadline) {
        if (-not (Get-AppProcess)) { return [int]((Get-Date) - $t0).TotalSeconds }
        Start-Sleep -Milliseconds 500
    }
    return -1
}

function Reset-Machine {
    # Leftover Autodesk helpers stop the next launch coming up at all - a crashed
    # iteration otherwise poisons the one after it. taskkill terminates rather
    # than faulting, so nothing here can write a dump of its own.
    try { Stop-TurboSession } catch { }
    foreach ($p in $ExeName, 'AcHelp2.exe', 'ADPClientService.exe', 'AdskAccessService.exe', 'AdskIdentityManager.exe') {
        Start-Process -FilePath 'taskkill.exe' -ArgumentList @('/f', '/im', $p, '/t') `
            -NoNewWindow -Wait -ErrorAction SilentlyContinue | Out-Null
    }
    Start-Sleep -Seconds 3
}

# ---------------------------------------------------------------------------
# Dumps
# ---------------------------------------------------------------------------
function Get-DumpSet {
    if (-not (Test-Path $DumpDir)) { return @() }
    @(Get-ChildItem -Path $DumpDir -Filter '*.dmp' -File -ErrorAction SilentlyContinue |
      ForEach-Object { $_.Name })
}

function Wait-DumpsSettled {
    # WerFault writes the dump after the faulting process is already gone.
    Start-Sleep -Seconds 5
    $deadline = (Get-Date).AddSeconds($PostCrashGraceSec)
    while ((Get-Date) -lt $deadline) {
        if (-not (Get-Process -Name WerFault, WerFaultSecure -ErrorAction SilentlyContinue)) { break }
        Start-Sleep -Seconds 2
    }
    Get-DumpSet
}

function Test-DumpSignature {
    param([string]$Path)
    if ($SkipDumpAnalysis) { return $null }
    $cdb = Get-ChildItem -Path `
        'C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\cdb.exe', `
        'C:\Program Files\Windows Kits\10\Debuggers\x64\cdb.exe' -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if (-not $cdb) { return $null }
    $out = & $cdb.FullName -z $Path -c '.symfix; .reload; !analyze -v; q' 2>&1 | Out-String
    $bucket = ([regex]'FAILURE_BUCKET_ID:\s*(\S+)').Match($out).Groups[1].Value
    if ($bucket) { return $bucket }
    return 'unknown'
}

# ---------------------------------------------------------------------------
# One iteration
# ---------------------------------------------------------------------------
function Invoke-Iteration {
    param([int]$Index, [string[]]$Seen)

    Write-Step "iteration $Index/$Iterations  mode=$Mode  delay=${SecondCloseDelayMs}ms"
    Reset-Machine
    Start-App

    $proc = Wait-AppReady
    if (-not $proc) {
        Write-Warning "  app never became ready - iteration skipped"
        return [pscustomobject]@{ Index = $Index; Result = 'skipped'; Pid = $null; Dumps = @(); ExitSec = $null }
    }
    $pid0 = $proc.Id
    Write-Step "  ready, pid $pid0, $((Get-AppWindows -TargetPid $pid0).Count) top-level window(s)"

    if (-not (Close-MainWindow -TargetPid $pid0)) {
        return [pscustomobject]@{ Index = $Index; Result = 'skipped'; Pid = $pid0; Dumps = @(); ExitSec = $null }
    }

    $exitSec = $null
    switch ($Mode) {
        'TurboStop' {
            Start-Sleep -Milliseconds $SecondCloseDelayMs
            Write-Step "  close #2 -> turbo stop $SessionName"
            Stop-TurboSession
            $exitSec = Wait-ProcessGone
        }
        'TurboStopAfter' {
            # Control: let the app finish its own exit, so the two teardowns
            # cannot overlap. The stop that follows has nothing left to close.
            $exitSec = Wait-ProcessGone
            Write-Step "  app exited after ${exitSec}s, only then: turbo stop"
            Stop-TurboSession
        }
        'Native' {
            Start-Sleep -Milliseconds $SecondCloseDelayMs
            if (Get-AppProcess) { [void](Send-WmCloseBroadcast -TargetPid $pid0) }
            else { Write-Warning "  app already gone before close #2 - lower -SecondCloseDelayMs" }
            $exitSec = Wait-ProcessGone
        }
    }

    $after = Wait-DumpsSettled
    $new = @($after | Where-Object { $Seen -notcontains $_ })

    if ($new.Count -gt 0) {
        foreach ($d in $new) {
            $sig = Test-DumpSignature -Path (Join-Path $DumpDir $d)
            Write-Host ("  CRASH: {0}{1}" -f $d, $(if ($sig) { "  [$sig]" } else { "" })) -ForegroundColor Red
        }
        $res = 'crash'
    } else {
        Write-Host "  clean exit (${exitSec}s)" -ForegroundColor Green
        $res = 'clean'
    }
    return [pscustomobject]@{ Index = $Index; Result = $res; Pid = $pid0; Dumps = $new; ExitSec = $exitSec }
}

# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if ($Mode -ne 'Native' -and -not (Get-Command turbo.exe -ErrorAction SilentlyContinue)) {
    throw "turbo.exe not on PATH (needed for mode $Mode)."
}

Enable-WerLocalDumps
$records = @()
try {
    $seen = Get-DumpSet
    for ($i = 1; $i -le $Iterations; $i++) {
        $r = Invoke-Iteration -Index $i -Seen $seen
        $records += $r
        $seen = Get-DumpSet
    }
} finally {
    Reset-Machine
    Restore-WerLocalDumps
}

$crashed = @($records | Where-Object { $_.Result -eq 'crash' }).Count
$clean   = @($records | Where-Object { $_.Result -eq 'clean' }).Count
$skipped = @($records | Where-Object { $_.Result -eq 'skipped' }).Count

Write-Host ""
Write-Host "===== $Mode, delay ${SecondCloseDelayMs}ms =====" -ForegroundColor Cyan
Write-Host "  crashed : $crashed / $($crashed + $clean) measured iteration(s)"
Write-Host "  clean   : $clean"
if ($skipped) { Write-Host "  skipped : $skipped (app never became ready)" }
Write-Host "  dumps   : $DumpDir"
Write-Host ""
Write-Host "Expected from CI: TurboStop ~50%, TurboStopAfter 0/27." -ForegroundColor DarkGray
Write-Host "A crash in Native mode means no container is needed to provoke it." -ForegroundColor DarkGray

$records | Format-Table Index, Result, Pid, ExitSec, @{n='Dumps';e={$_.Dumps -join ','}} -AutoSize
