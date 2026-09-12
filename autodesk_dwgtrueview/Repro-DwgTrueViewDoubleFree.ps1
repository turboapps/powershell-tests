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

.PARAMETER Iterations
    Maximum attempts. The run STOPS at the first attempt that produces a dump -
    one dump is all you need, and continuing would only pile up 800 MB files and
    hand the next attempt a machine with a crashed instance on it.

.PARAMETER DumpDir
    Override where dumps are read from. By default nothing is moved: the script
    enables WER LocalDumps without setting DumpFolder, so dumps land wherever
    they already would - the box's own DumpFolder if it configures one, else
    Windows' default %LOCALAPPDATA%\CrashDumps.

.PARAMETER SecondCloseDelayMs
    Gap between the first close and the second. In CI the Alt+F4 -> `turbo stop`
    gap was 1.3 s and 2.3 s, and the crash followed ~4 s later. The app exits in
    about 2 s, so the window is narrow - sweep this if a mode will not reproduce.

.EXAMPLE
    .\Repro-DwgTrueViewDoubleFree.ps1 -Mode TurboStop -Iterations 10
    Up to 10 attempts, stopping at the first dump. CI crashes on roughly half of
    them, so this usually stops within two or three.

.EXAMPLE
    .\Repro-DwgTrueViewDoubleFree.ps1 -Mode Native -Iterations 10
    Crashes here => an Autodesk defect any WM_CLOSE broadcast can trigger.
    Clean here while TurboStop crashes => something about the container matters.
    Give this one a decent -Iterations before believing a clean result: it is a
    race, so 10 clean attempts is far weaker evidence than a single crash.

.EXAMPLE
    foreach ($d in 400,800,1200,1600,2000,2400) {
        .\Repro-DwgTrueViewDoubleFree.ps1 -Mode Native -Iterations 5 -SecondCloseDelayMs $d
    }
    Sweep for the timing window.

.NOTES
    Run elevated: WER LocalDumps lives under HKLM. The script only forces
    DumpType (full - a minidump will not show the corrupted CStringData) and
    DumpCount, never DumpFolder, and it puts the previous values back on exit
    unless -KeepWerSettings is given.
#>
[CmdletBinding()]
param(
    [ValidateSet('TurboStop', 'TurboStopAfter', 'Native')]
    [string]$Mode = 'TurboStop',

    # Maximum attempts. The run stops as soon as one produces a dump.
    [int]$Iterations = 10,
    [int]$SecondCloseDelayMs = 1500,

    [string]$Image = 'autodesk/dwgtrueview',
    [string]$SessionName = 'dwgrepro',
    [string]$XvmVersion = '',

    # Empty = wherever WER LocalDumps already writes: the box's own DumpFolder
    # if it sets one, otherwise Windows' default, %LOCALAPPDATA%\CrashDumps.
    [string]$DumpDir = '',
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
$script:ResolvedDumpDir = $null

function Enable-WerLocalDumps {
    $id = [Security.Principal.WindowsIdentity]::GetCurrent()
    if (-not (New-Object Security.Principal.WindowsPrincipal $id).IsInRole(
              [Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "Run elevated: WER LocalDumps is under HKLM."
    }
    if (Test-Path $WerKey) {
        $script:WerSaved = Get-ItemProperty -Path $WerKey
    } else {
        New-Item -Path $WerKey -Force | Out-Null
    }
    # DumpFolder is deliberately NOT set - dumps stay wherever WER already puts
    # them. Only the dump TYPE is forced: the default is a minidump, and the
    # CStringData this bug double-frees is only readable in a full one.
    New-ItemProperty -Path $WerKey -Name DumpType  -Value 2  -PropertyType DWord -Force | Out-Null
    New-ItemProperty -Path $WerKey -Name DumpCount -Value 20 -PropertyType DWord -Force | Out-Null
    # No modal WER dialog: one would wedge an unattended run.
    New-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting' `
        -Name DontShowUI -Value 1 -PropertyType DWord -Force | Out-Null

    $script:ResolvedDumpDir = Resolve-WerDumpFolder
    New-Item -ItemType Directory -Path $script:ResolvedDumpDir -Force | Out-Null
    Write-Step "WER LocalDumps: full dumps -> $script:ResolvedDumpDir"
}

# Where WER will actually write. An explicit -DumpDir wins; otherwise the box's
# own DumpFolder if it configures one (REG_EXPAND_SZ, so expand it); otherwise
# Windows' default for LocalDumps, %LOCALAPPDATA%\CrashDumps.
#
# That default is per-user: the dump lands in the LOCALAPPDATA of whoever the
# CRASHING process runs as. Here that is this same user - the container runs
# --isolate=merge-user as the caller, and Native mode is a plain child process -
# so watching our own LOCALAPPDATA is right. It would not be if the app were
# ever run as a service or as another user.
function Resolve-WerDumpFolder {
    if ($DumpDir) { return $DumpDir }
    $configured = (Get-ItemProperty -Path $WerKey -Name DumpFolder -ErrorAction SilentlyContinue).DumpFolder
    if ($configured) { return [Environment]::ExpandEnvironmentVariables($configured) }
    return (Join-Path $env:LOCALAPPDATA 'CrashDumps')
}

function Restore-WerLocalDumps {
    if ($KeepWerSettings) { Write-Step "Leaving WER settings in place (-KeepWerSettings)"; return }
    try {
        if ($null -eq $script:WerSaved) {
            Remove-Item -Path $WerKey -Recurse -Force -ErrorAction SilentlyContinue
        } else {
            # DumpFolder is absent from this list on purpose: never touched.
            foreach ($n in 'DumpType', 'DumpCount') {
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
    Invoke-Turbo $turboArgs
}

# Never `Start-Process -Wait` for turbo.
#
# -Wait does not wait for the launched process: it waits on a job object holding
# that process AND every descendant. `turbo try -d` deliberately leaves a
# `turbo start <session>` behind to host the container, so the job never
# completes while the container is up and -Wait never returns. On os-test3 this
# hung the very first launch: the app came up fine and settled on the Start tab,
# and the script sat there for 11 minutes having printed nothing past
# "Running new session dwgrepro#158acfb0".
#
# The CI test never hit this because it launches with subprocess.Popen and does
# not wait at all. -PassThru plus WaitForExit waits for turbo itself and nothing
# it spawned, which is what was meant.
function Invoke-Turbo {
    param([string[]]$TurboArgs, [int]$TimeoutSec = 900)
    $p = Start-Process -FilePath 'turbo.exe' -ArgumentList $TurboArgs -NoNewWindow -PassThru
    if (-not $p.WaitForExit($TimeoutSec * 1000)) {
        Write-Warning "turbo $($TurboArgs[0]) still running after $TimeoutSec s - continuing"
    }
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
    $windowed = $false
    while ((Get-Date) -lt $deadline) {
        $proc = Get-AppProcess
        if ($proc) {
            $titled = @(Get-AppWindows -TargetPid $proc.Id | Where-Object { $_.Visible -and $_.Title })
            if ($titled.Count -gt 0) { $windowed = $true; break }
        }
        Start-Sleep -Milliseconds 500
    }
    # Both conditions matter. Falling out of the loop on the deadline used to
    # leave $proc set and report the app ready, which would have closed an app
    # that never finished coming up.
    if (-not $proc -or -not $windowed) { return $null }

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
    Invoke-Turbo @('stop', $SessionName) -TimeoutSec 180
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
    if (-not $script:ResolvedDumpDir -or -not (Test-Path $script:ResolvedDumpDir)) { return @() }
    # Only our image. Now that dumps go to the shared per-user CrashDumps folder
    # rather than a private one, anything else on the box that faults mid-run
    # would otherwise be counted as this app crashing. WER names them
    # <image>.<pid>.dmp, so the pid still attributes each one to its attempt.
    @(Get-ChildItem -Path $script:ResolvedDumpDir -Filter "$ExeName.*.dmp" -File -ErrorAction SilentlyContinue |
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
            $sig = Test-DumpSignature -Path (Join-Path $script:ResolvedDumpDir $d)
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
        # One dump is the whole point: stop and leave the machine and the dump
        # alone for analysis rather than piling up 800 MB files and giving the
        # next iteration a crashed instance to start from.
        if ($r.Result -eq 'crash') {
            Write-Step "reproduced on attempt $i - stopping"
            break
        }
        $seen = Get-DumpSet
    }
} finally {
    Reset-Machine
    Restore-WerLocalDumps
}

$crashRec = @($records | Where-Object { $_.Result -eq 'crash' }) | Select-Object -First 1
$clean    = @($records | Where-Object { $_.Result -eq 'clean' }).Count
$skipped  = @($records | Where-Object { $_.Result -eq 'skipped' }).Count

Write-Host ""
Write-Host "===== $Mode, delay ${SecondCloseDelayMs}ms =====" -ForegroundColor Cyan
if ($crashRec) {
    Write-Host "  REPRODUCED on attempt $($crashRec.Index) (after $clean clean attempt(s))" -ForegroundColor Red
    foreach ($d in $crashRec.Dumps) {
        Write-Host "  dump    : $(Join-Path $script:ResolvedDumpDir $d)"
    }
} else {
    Write-Host "  not reproduced in $clean measured attempt(s)" -ForegroundColor Green
    Write-Host "  dumps   : $script:ResolvedDumpDir (empty of new dumps)"
}
if ($skipped) { Write-Host "  skipped : $skipped (app never became ready)" }
Write-Host ""
Write-Host "Expected from CI: TurboStop ~50% per attempt, TurboStopAfter 0/27." -ForegroundColor DarkGray
Write-Host "A crash in Native mode means no container is needed to provoke it." -ForegroundColor DarkGray
Write-Host "Not reproducing is weak evidence on its own - this is a race; try more" -ForegroundColor DarkGray
Write-Host "attempts and sweep -SecondCloseDelayMs before concluding anything." -ForegroundColor DarkGray

$records | Format-Table Index, Result, Pid, ExitSec, @{n='Dumps';e={$_.Dumps -join ','}} -AutoSize
