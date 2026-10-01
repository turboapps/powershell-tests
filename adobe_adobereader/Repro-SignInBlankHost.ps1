<#
.SYNOPSIS
  Minimal repro for the blank Adobe sign-in window in 32-bit Acrobat Reader under the Turbo VM.

.DESCRIPTION
  One iteration = launch adobe/adobereader (32-bit) with the App Tests flags, click Sign in,
  and watch for RdrCEF.exe (the CEF host) exiting with 0x80000003 STATUS_BREAKPOINT. That exit
  is what leaves the sign-in window blank (applab runs 36608527985, 36613923922, 36618879543:
  7 breakpoint exits each, all within seconds of the Sign-in click). No SikuliX, no credentials.

  Needs an interactive desktop and elevation (WMI process-stop events).
  Exit code: 1 = reproduced, 0 = not reproduced within -MaxIterations, 2 = the script itself failed.
#>
param(
    [string]$Xvm = '',                 # e.g. 26.9.56; empty = latest local VM
    [string]$VmPackage = '',           # path to an xvm-turbo-x64.exe to import during prep
    [bool]$Diagnostic = $true,         # --diagnostic; on a hit the xclogs are copied out
    [int]$MaxIterations = 0,           # 0 = until reproduced
    [switch]$SkipPrep,
    [string]$OutRoot = $PSScriptRoot,
    [int]$ContainerKeepCount = 5,
    [int]$WaitSeconds = 60,            # how long to watch after the Sign-in click
    [switch]$ViaShortcut,              # launch like the App Test does: turbo installi + Start menu shortcut
    [switch]$F1First,                  # press F1 (Reader help opens Edge in the container) before Sign in
    [string]$OpenPdf = '',             # PDF to open (Ctrl+O) before Sign in, e.g. the test's homeacrordrunified18_2025.pdf
    [switch]$StopHostEdge,             # stop the host's msedge first: with merge-user, a running host Edge takes over
                                       # the container's Edge launch, so Edge never runs inside the container
    [switch]$TouchFonts                # before Sign in, from a second process in the same container, open every
                                       # C:\WINDOWS\Fonts file and duplicate its handle into Reader - what in-container
                                       # Edge does when it hands fonts to its renderers, and what makes the VM fault the
                                       # file into the sandbox
)
$ErrorActionPreference = 'Stop'
$Image = 'adobe/adobereader:26.002.21931'
$Name = 'signinrepro'
$Breakpoint = [uint32]2147483651       # 0x80000003
New-Item -ItemType Directory -Force $OutRoot | Out-Null

function Log([string]$m) { $l = '[{0:HH:mm:ss}] {1}' -f (Get-Date), $m; Write-Host $l; Add-Content "$OutRoot\repro.log" $l }
trap { Log "ERROR (line $($_.InvocationInfo.ScriptLineNumber)): $_"; try { Snap "$OutRoot\error.png" } catch { }; exit 2 }

# Start-Process + file redirection, never a pipe: turbo run's detached child inherits handles
# and would hold a pipe open for the container's lifetime.
function Turbo([string]$a, [int]$sec = 900) {
    $o = Join-Path $env:TEMP "signinrepro-$PID.out"
    $p = Start-Process turbo.exe -ArgumentList $a -NoNewWindow -PassThru -RedirectStandardOutput $o -RedirectStandardError "$o.err"
    if (-not $p.WaitForExit($sec * 1000)) { $p.Kill(); throw "turbo $a timed out after $sec s" }
    (Get-Content $o, "$o.err" -ErrorAction SilentlyContinue) -join "`n"
}

Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes, System.Windows.Forms, System.Drawing
Add-Type -Namespace W -Name U -MemberDefinition @'
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
[DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
[DllImport("user32.dll")] public static extern void mouse_event(int f, int x, int y, int d, int e);
'@
$UIA = [System.Windows.Automation.AutomationElement]
$Tree = [System.Windows.Automation.TreeScope]
$All = [System.Windows.Automation.Condition]::TrueCondition

function Snap([string]$path) {
    $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
    $bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
    [System.Drawing.Graphics]::FromImage($bmp).CopyFromScreen(0, 0, 0, 0, $bmp.Size); $bmp.Save($path); $bmp.Dispose()
}

function Sessions { $j = Turbo 'sessions --format=json' 60 | ConvertFrom-Json; @($j[0].result.containers) }

if (-not $SkipPrep) {
    Log 'prep: WER full dumps, image pulls, VM import'
    $wer = 'HKLM:\SOFTWARE\Microsoft\Windows\Windows Error Reporting'
    New-Item -Force "$wer\LocalDumps" | Out-Null
    Set-ItemProperty "$wer\LocalDumps" DumpType 2 -Type DWord
    Set-ItemProperty $wer DontShowUI 1 -Type DWord
    Log (Turbo "pull $Image")
    Log (Turbo 'pull turbobuild/isolate-edge-wc')
    if ($VmPackage) { Log (Turbo "import vm `"$VmPackage`"") }
}

$vmFlag = if ($Xvm) { " --vm=$Xvm" } else { '' }
$diagFlag = if ($Diagnostic) { ' --diagnostic' } else { '' }
$flags = "--enable=disablefontpreload,usedllinjection,cachefileinfo --network=$Name --disable-proxy-resolve-via-proxy " +
         "--using=turbobuild/isolate-edge-wc --isolate=merge-user$vmFlag$diagFlag"
$launch = "run $Image --name=$Name $flags -d"
$shortcut = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Acrobat Reader.lnk"
if ($ViaShortcut) { Log (Turbo "installi $Image --offline $flags" 600) }
# --isolate=merge-user shows the container only the user profile, so the PDF is copied to the Desktop.
$pdf = "$env:USERPROFILE\Desktop\signin-repro.pdf"
if ($OpenPdf) { Copy-Item $OpenPdf $pdf -Force }

for ($i = 1; $MaxIterations -eq 0 -or $i -le $MaxIterations; $i++) {
    foreach ($s in 'start', 'stop') {
        Unregister-Event "rdrcef-$s" -ErrorAction SilentlyContinue
        Register-CimIndicationEvent -SourceIdentifier "rdrcef-$s" -Query "SELECT * FROM Win32_Process$($s)Trace WHERE ProcessName='RdrCEF.exe'"
    }
    if ($StopHostEdge) {
        $n = @(Get-Process msedge -ErrorAction SilentlyContinue).Count
        Get-Process msedge -ErrorAction SilentlyContinue | Stop-Process -Force; Start-Sleep 3
        Log "stopped $n host msedge process(es); $(@(Get-Process msedge -ErrorAction SilentlyContinue).Count) left"
    }
    if ($ViaShortcut) { Log "iteration $i : explorer $shortcut"; Start-Process explorer.exe "`"$shortcut`"" }
    else { Log "iteration $i : turbo $launch"; Log (Turbo $launch 300) }

    # Reader's main window and its top-right command cluster (help, bell, apps, Sign in). The
    # cluster is built once Home has loaded, so poll for both.
    $win = $cluster = $null
    for ($t = 0; $t -lt 60 -and -not $cluster; $t++) {
        Start-Sleep 3
        $win = $UIA::RootElement.FindAll($Tree::Children, $All) | Where-Object { $_.Current.ClassName -eq 'AcrobatSDIWindow' } | Select-Object -First 1
        if ($win) {
            $cluster = $win.FindAll($Tree::Descendants, $All) | Where-Object { $_.Current.Name -eq 'AVUITopRightCommandCluster' } |
                Where-Object { $_.Current.BoundingRectangle.X -gt $win.Current.BoundingRectangle.X + 300 } | Select-Object -First 1
        }
    }
    if (-not $cluster) { throw "Sign-in cluster (AVUITopRightCommandCluster) not found (main window seen: $([bool]$win))" }
    Start-Sleep 5
    $UIA::RootElement.FindAll($Tree::Children, $All) |
        Where-Object { $_.Current.ClassName -in 'CASCADIA_HOSTING_WINDOW_CLASS', 'ConsoleWindowClass' } |
        ForEach-Object { [W.U]::ShowWindow([IntPtr]$_.Current.NativeWindowHandle, 6) | Out-Null }   # SW_MINIMIZE
    [W.U]::SetForegroundWindow([IntPtr]$win.Current.NativeWindowHandle) | Out-Null
    Start-Sleep 1
    if ($OpenPdf) {
        Log "opening $pdf (Ctrl+O)"
        [System.Windows.Forms.SendKeys]::SendWait('^o'); Start-Sleep 5
        [System.Windows.Forms.SendKeys]::SendWait($pdf); Start-Sleep 1
        [System.Windows.Forms.SendKeys]::SendWait('{ENTER}'); Start-Sleep 15
        Snap "$OutRoot\iteration-$i-pdf.png"
        [W.U]::SetForegroundWindow([IntPtr]$win.Current.NativeWindowHandle) | Out-Null; Start-Sleep 1
    }
    if ($TouchFonts) {
        # A second turbo run against the running container starts the process inside it.
        $cmd = @'
Add-Type -Namespace K -Name D -MemberDefinition '[DllImport("kernel32.dll")] public static extern System.IntPtr OpenProcess(uint a, bool i, int p);
[DllImport("kernel32.dll")] public static extern bool DuplicateHandle(System.IntPtr sp, System.IntPtr sh, System.IntPtr tp, out System.IntPtr th, uint a, bool i, uint o);'
$reader = Get-Process AcroRd32 | Where-Object MainWindowHandle -ne 0 | Select-Object -First 1
$tp = [K.D]::OpenProcess(0x40, $false, $reader.Id)
$self = [Diagnostics.Process]::GetCurrentProcess().Handle
$n = 0
Get-ChildItem $env:windir\Fonts -File | ForEach-Object {
    try {
        $fs = [IO.File]::OpenRead($_.FullName); $out = [IntPtr]::Zero
        if ([K.D]::DuplicateHandle($self, $fs.SafeFileHandle.DangerousGetHandle(), $tp, [ref]$out, 0, $false, 2)) { $n++ }
        $fs.Close()
    } catch { }
}
"duplicated $n font handles into AcroRd32 $($reader.Id)"
'@
        $enc = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($cmd))
        Log 'opening every font file from a process inside the container'
        Log (Turbo "run $Image --name=$Name $flags --startup-file=powershell.exe -- -NoProfile -EncodedCommand $enc" 300)
        Start-Sleep 5
        [W.U]::SetForegroundWindow([IntPtr]$win.Current.NativeWindowHandle) | Out-Null; Start-Sleep 1
    }
    if ($F1First) {
        Log 'pressing F1 (help opens in Edge)'
        [System.Windows.Forms.SendKeys]::SendWait('{F1}')
        Start-Sleep 30
        Snap "$OutRoot\iteration-$i-f1.png"
        Log "after F1: $(@(Get-Process msedge -ErrorAction SilentlyContinue).Count) msedge process(es) running"
        [W.U]::SetForegroundWindow([IntPtr]$win.Current.NativeWindowHandle) | Out-Null
        Start-Sleep 2
    }
    $r = $cluster.Current.BoundingRectangle
    $x = [int]($r.Right - 38); $y = [int]($r.Y + $r.Height / 2)   # "Sign in" is the cluster's right-most item
    Get-Event -ErrorAction SilentlyContinue | Where-Object SourceIdentifier -like 'rdrcef-*' | Remove-Event
    Log "clicking Sign in at $x,$y"
    [W.U]::SetCursorPos($x, $y) | Out-Null; [W.U]::mouse_event(2, 0, 0, 0, 0); [W.U]::mouse_event(4, 0, 0, 0, 0)

    Start-Sleep 8; Snap "$OutRoot\iteration-$i-click.png"
    Start-Sleep ($WaitSeconds - 8)
    $starts = @(Get-Event -SourceIdentifier rdrcef-start -ErrorAction SilentlyContinue).Count
    $stops = @(Get-Event -SourceIdentifier rdrcef-stop -ErrorAction SilentlyContinue | ForEach-Object { $_.SourceEventArgs.NewEvent })
    $bp = @($stops | Where-Object { [uint32]$_.ExitStatus -eq $Breakpoint })
    $shot = "$OutRoot\iteration-$i.png"; Snap $shot
    Log ("iteration $i : RdrCEF started after click=$starts, exited=$($stops.Count), exited 0x80000003=$($bp.Count) " +
         "(pids $(($bp | ForEach-Object { $_.ProcessID }) -join ','))")

    # The shortcut's session gets a generated name, so take the newest Reader session.
    $id = (Sessions | Where-Object { $_.runState -eq 'Running' -and ($_ | ConvertTo-Json -Depth 5) -match 'adobereader' } |
        Sort-Object { [datetime]$_.created } | Select-Object -Last 1).id
    if ($bp.Count -gt 0) {
        Log "REPRODUCED on iteration $i : $($bp.Count) RdrCEF process(es) exited with 0x80000003 after Sign in. Container $id left running."
        if ($Diagnostic -and $id) {
            $cfg = (Turbo 'config --format=json' 60 | ConvertFrom-Json)[0].result.configuration.containerStoragePath
            $root = if ($cfg -match 'sandboxes\\?$') { $cfg } else { Join-Path $cfg 'sandboxes' }
            Copy-Item "$root\$id\logs" "$OutRoot\hit-$i-xclogs" -Recurse -ErrorAction SilentlyContinue
            Log "xclogs copied to $OutRoot\hit-$i-xclogs"
        }
        exit 1
    }
    if ($starts -eq 0) { Log "iteration $i : no RdrCEF started after the click - the click missed Sign in; see $shot" }
    if ($Diagnostic -and $id) {   # what ran inside the container, from its xclogs, before they are removed
        $cfg = (Turbo 'config --format=json' 60 | ConvertFrom-Json)[0].result.configuration.containerStoragePath
        $root = if ($cfg -match 'sandboxes\\?$') { $cfg } else { Join-Path $cfg 'sandboxes' }
        $heads = Get-ChildItem "$root\$id\logs" -Filter 'xclog_*' -ErrorAction SilentlyContinue | ForEach-Object {
            [pscustomobject]@{ Head = (Get-Content $_.FullName -TotalCount 1); File = $_.FullName } }
        $edge = @($heads | Where-Object { $_.Head -match 'msedge\.exe|\\setup\.exe|powershell\.exe' }).Count
        $denied = @($heads | Where-Object { $_.Head -match 'RdrCEF\.exe.*--type=renderer' } |
            Where-Object { Select-String -Path $_.File -Pattern 'status:0xC0000022.*\\FONTS\\' -Quiet }).Count
        Log "iteration $i : in-container msedge/setup/powershell processes=$edge, RdrCEF renderers denied C:\WINDOWS\FONTS=$denied"
        if ($denied -gt 0) {   # a near miss is evidence too; keep its logs
            Copy-Item "$root\$id\logs" "$OutRoot\nearmiss-$i-xclogs" -Recurse -ErrorAction SilentlyContinue
            Log "iteration $i : xclogs kept in $OutRoot\nearmiss-$i-xclogs"
        }
    }
    if ($id) { Log (Turbo "stop $id" 120); Log (Turbo "rm $id" 120) }
    # Backstop for stale sessions from earlier runs.
    Sessions | Where-Object { $_.runState -ne 'Running' } |
        Sort-Object { [datetime]$_.created } -Descending | Select-Object -Skip $ContainerKeepCount |
        ForEach-Object { Log (Turbo "rm $($_.id)" 120) }
}
Log "not reproduced in $MaxIterations iteration(s)"
exit 0
