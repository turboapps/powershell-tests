$NewLine = [System.Environment]::NewLine

# Clean the environment for tests, pull test related images and login to a Turbo Server.
# Note: this funtion will remove all the Turbo sessions, unregister all the apps installed by Turbo and reset Turbo Client configurations.
function PrepareTest {
    param (
        [string]$image,
        [string]$secretsFile,
        [string]$localLogsDir,
        [string]$extra
    )
    if ([string]::IsNullOrWhiteSpace($secretsFile)) {
        $secretsFile = Join-Path $PSScriptRoot "secrets.txt"
    }
    if ([string]::IsNullOrWhiteSpace($localLogsDir)) {
        $localLogsDir = "$env:USERPROFILE\Desktop"
    }

    # Get the name string for the log file.
    $name = $image -replace '[/]', '_'
    Start-Transcript -Path "$localLogsDir\$name-executor.log"

    # Remove completion markers from a previous run so a stale marker is not
    # mistaken for this run's result when iterating (see Write-TestDoneMarker).
    Remove-Item "$env:USERPROFILE\Desktop\TEST-DONE-PASS" -Force -ErrorAction SilentlyContinue
    Remove-Item "$env:USERPROFILE\Desktop\TEST-DONE-FAIL" -Force -ErrorAction SilentlyContinue

    # Per-step screenshots from a previous run (written by util.pre_test's hooks
    # to <Desktop>\<app>-steps). Numbering restarts at 001 each run, so stale
    # frames would be overwritten piecemeal and the leftovers mixed into what
    # the CI harness stages as this run's frames.
    Remove-Item "$env:USERPROFILE\Desktop\$name-steps" -Recurse -Force -ErrorAction SilentlyContinue

    # Turbo VM logs from a previous run (see CollectVmLogs), for the same reason.
    Remove-Item "$env:USERPROFILE\Desktop\$name-vm-logs" -Recurse -Force -ErrorAction SilentlyContinue

    # Extra turbo flags for tests that launch turbo themselves (from a Command
    # Prompt or a subprocess) rather than through TryTurboApp/RunTurboApp: the
    # test appends util.read_extra() to its command line. Written whenever the
    # caller passes -extra, empty included, so a stale file from a previous run
    # never leaks flags into this one.
    if ($PSBoundParameters.ContainsKey('extra')) {
        Set-Content -Path "$PSScriptRoot\..\$name\extra.txt" -Value $extra -ErrorAction SilentlyContinue
    }

    # Parse the secrets file.
    $secrets = Get-Content $secretsFile | ConvertFrom-Csv -Header "Key", "Value"
    $domain = $secrets | Where-Object { $_.Key -eq "Domain" } | Select-Object -ExpandProperty Value
    $apiKey = $secrets | Where-Object { $_.Key -eq "APIKey" } | Select-Object -ExpandProperty Value

    # Stop all Turbo sessions.
    turbo stop -a

    # Remove all Turbo sessions.
    turbo rm -a

    # Uninstall all the apps installed by Turbo Client.
    turbo uninstalli -a

    # Reset client config
    turbo config --reset

    # Pull the base and xvm images from hub.turbo.net
    turbo pull /xvm --format=json
    turbo pull base --format=json

    # Point to the specified Turbo Server and log in.
    if (-not [string]::IsNullOrWhiteSpace($domain)) {
        turbo config --domain $domain
    } else {
        Write-Host "Domain not found in secrets.txt"
        Exit 1
    }

    if (-not [string]::IsNullOrWhiteSpace($apiKey)) { # API key is required except for https://turbo.net.
        turbo login --api-key $apiKey
    } else {
        Write-Host "API key not found in secrets.txt"
    }

    # Pull test related images. There won't be test under full isolation, so no need to pull clean.
    turbo pull sikulix/sikulixide --format=json
    turbo pull oracle/jre-x64 --format=json
}

# Pull Turbo images (app image and images in the `--using` list).
function PullTurboImages {
    param (
        [string]$image,
        [string]$using
    )

    turbo pull $image --format=json

    if (-not [string]::IsNullOrWhiteSpace($using)) {
        $using.Split(",") | ForEach-Object {
            turbo pull $_.Trim() --format=json
        }
    }
}

# Install apps using Turbo Client.
function InstallTurboApp {
    param (
        [string]$image,
        [string]$using,
        [string]$isolate,
        [string]$extra
    )

    $command = "turbo installi $image --offline --enable=disablefontpreload,usedllinjection,cachefileinfo --network=test --disable-proxy-resolve-via-proxy"

    #Construct the Turbo command.
    if (-not [string]::IsNullOrWhiteSpace($using)) {
        $command += " --using=$using"
    }

    if (-not [string]::IsNullOrWhiteSpace($isolate)) {
        $command += " --isolate=$isolate"
    }

    if (-not [string]::IsNullOrWhiteSpace($extra)) {
        $command = $command + " " + $extra
    }

    Invoke-Expression $command
}

# Run a process.
# Return process exit code if shouldWait is $True.
function RunProcess {
    param (
        [string]$path,
        [string]$arguments = "",
        [bool]$shouldWait = $False
    )

    Write-Host "$($NewLine)Executing: $path $arguments"

    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = $path
    $processInfo.Arguments = $arguments
    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $ProcessInfo
    $process.Start() | Out-Null # Pipe out the "True" message, so that only process exit code is returned.

    If ($shouldWait) {
        Write-Host "Waiting for process to finish..."
        $process.WaitForExit()
        Write-Host "Process finished with exit code $($Process.ExitCode)"
        Return $process.ExitCode
    }
}

# Run `turbo try` command for the app (image). Unlike `turbo run`, `turbo try` runs a temporary session, and is used here to simplify the test.
function TryTurboApp {
    param (
        [string]$image,
        [string]$using,
        [string]$isolate,
        [string]$extra,
        [bool]$detached = $True
    )

    $command = "try $image --name=test --enable=disablefontpreload,usedllinjection,cachefileinfo --network=test --disable-proxy-resolve-via-proxy"

    # Construct the Turbo command.
    if (-not [string]::IsNullOrWhiteSpace($using)) {
        $command += " --using=$using"
    }
    
    if (-not [string]::IsNullOrWhiteSpace($isolate)) {
        $command += " --isolate=$isolate"
    }

    # In detached mode, this function should not blocking the program from running.
    if ($detached) {
        $command += " -d"
    }

    if (-not [string]::IsNullOrWhiteSpace($extra)) {
        $command = $command + " " + $extra
    }

    RunProcess -path "turbo.exe" -arguments $command -shouldWait (-not $detached)
}

# Run `turbo run` command for the app (image).
function RunTurboApp {
    param (
        [string]$image,
        [string]$using,
        [string]$isolate,
        [string]$extra,
        [bool]$detached = $True
    )

    $command = "run $image --enable=disablefontpreload,usedllinjection,cachefileinfo --network=test --disable-proxy-resolve-via-proxy"

    # Construct the Turbo command.
    if (-not [string]::IsNullOrWhiteSpace($using)) {
        $command += " --using=$using"
    }

    if (-not [string]::IsNullOrWhiteSpace($isolate)) {
        $command += " --isolate=$isolate"
    }

    # In detached mode, this function should not blocking the program from running.
    if ($detached) {
        $command += " -d"
    }

    if (-not [string]::IsNullOrWhiteSpace($extra)) {
        $command = $command + " " + $extra
    }

    RunProcess -path "turbo.exe" -arguments $command -shouldWait (-not $detached)
}

# Hide the PowerShell prompt window.
function HidePowerShellWindow {
# Define a type that includes the necessary Windows API functions.
Add-Type @"
    using System;
    using System.Runtime.InteropServices;

    public class WindowHandler {
        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        [DllImport("kernel32.dll")]
        public static extern IntPtr GetConsoleWindow();

        public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

        [DllImport("user32.dll")]
        public static extern bool EnumWindows(EnumWindowsProc callback, IntPtr lParam);

        [DllImport("user32.dll")]
        public static extern bool IsWindowVisible(IntPtr hWnd);

        [DllImport("user32.dll")]
        public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);
    }
"@

    # Constant for minimizing the window.
    $SW_MINIMIZE = 6

    # Get the window handle for the console.
    $consoleHandle = [WindowHandler]::GetConsoleWindow()

    # Minimize the window.
    [WindowHandler]::ShowWindow($consoleHandle, $SW_MINIMIZE)

    # On Windows 11 24H2 the default terminal is Windows Terminal, which hosts
    # this PowerShell in a ConPTY. GetConsoleWindow() then returns the hidden
    # pseudoconsole window rather than the visible Windows Terminal frame, and
    # Shell.Application.MinimizeAll() does not minimize Windows Terminal windows,
    # so the terminal stays on top and covers the app under test - every sikuli
    # image match then fails. Minimize the top-level Windows Terminal windows
    # explicitly so the desktop is clear for the visual test.
    $terminalPids = @(Get-Process -Name "WindowsTerminal" -ErrorAction SilentlyContinue |
        Select-Object -ExpandProperty Id)
    if ($terminalPids.Count -gt 0) {
        $callback = [WindowHandler+EnumWindowsProc]{
            param($hWnd, $lParam)
            if ([WindowHandler]::IsWindowVisible($hWnd)) {
                $windowPid = 0
                [void][WindowHandler]::GetWindowThreadProcessId($hWnd, [ref]$windowPid)
                if ($terminalPids -contains $windowPid) {
                    [void][WindowHandler]::ShowWindow($hWnd, $SW_MINIMIZE)
                }
            }
            return $true
        }
        [void][WindowHandler]::EnumWindows($callback, [IntPtr]::Zero)
    }

    # Show the Desktop
    (New-Object -ComObject Shell.Application).MinimizeAll()

    CloseStartMenu
    # Kill any OneDrive processes
    taskkill /F /IM "onedrive*" /T
    ConfigureDefender
}

# Configure Windows Defender settings
function ConfigureDefender {

    # Disable Cloud-delivered protection
    Set-MpPreference -MAPSReporting Disabled
    # Disable Automatic sample submission
    Set-MpPreference -SubmitSamplesConsent NeverSend

}

# Close the start menu
function CloseStartMenu {
# Define a type that includes the necessary Windows API functions.
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;

public class Keyboard {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, IntPtr dwExtraInfo);

    public const int KEYEVENTF_KEYDOWN = 0x0000;
    public const int KEYEVENTF_KEYUP = 0x0002;
    public const byte VK_ESCAPE = 0x1B;
}
"@ -PassThru

    # Close Start Menu
    [Keyboard]::keybd_event([Keyboard]::VK_ESCAPE, 0, [Keyboard]::KEYEVENTF_KEYDOWN, [IntPtr]::Zero)
    [Keyboard]::keybd_event([Keyboard]::VK_ESCAPE, 0, [Keyboard]::KEYEVENTF_KEYUP, [IntPtr]::Zero)

}

# Turbo VM logs.
#
# A container started with --diagnostic (the CI harness's vm_diagnostics run
# passes it in -extra) writes its VM diagnostic log to
# <sandbox>\logs\xclog_0x<pid>.txt. The client deletes and recreates that
# folder every time the same container starts again, so a launch's logs
# survive only if they are copied out before the next launch. They are copied
# at the two points where a session is known to have ended, not by polling:
# util.check_running() after a session terminated mid-test, and here after the
# sikulix test returned - which also covers a failure, where the app's session
# is usually still running with its dialogs on screen.
#
# Layout: <Desktop>\<app>-vm-logs\<container id>\<logs tree>. The CI harness
# (applab Invoke-AppTest.ps1) stages that folder as the <app>-vm-logs artifact.
# Only sandboxes holding an xclog_* file are copied, so on a run without
# --diagnostic this is one directory listing and nothing else. An existing copy
# is overwritten when the source is the same file grown, and kept as
# <name>.1, .2, ... when a different file has reappeared under the same name
# (pid reuse across launches). util.collect_vm_logs() implements the same rule.
# Best-effort: never changes the test result.
function CollectVmLogs {
    param (
        [string]$image
    )
    $name = $image -replace '[/]', '_'
    $destRoot = "$env:USERPROFILE\Desktop\$name-vm-logs"

    # `turbo config --reset` (PrepareTest) leaves the default location; honour a
    # relocated storage path anyway when the client reports one.
    $root = "$env:LOCALAPPDATA\Turbo\Containers\sandboxes"
    try {
        $cfg = (turbo config --format=json 2>$null | Out-String | ConvertFrom-Json)[0].result.configuration
        if ($cfg.containerStoragePath) { $root = [Environment]::ExpandEnvironmentVariables($cfg.containerStoragePath) }
    } catch { }
    if (-not (Test-Path -LiteralPath $root)) { return }

    foreach ($sb in @(Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue)) {
        $logs = Join-Path $sb.FullName 'logs'
        if (-not (Test-Path -LiteralPath $logs)) { continue }
        if (-not @(Get-ChildItem -LiteralPath $logs -Filter 'xclog_*' -File -ErrorAction SilentlyContinue)) { continue }
        foreach ($f in @(Get-ChildItem -LiteralPath $logs -File -Recurse -ErrorAction SilentlyContinue)) {
            $dst = Join-Path (Join-Path $destRoot $sb.Name) $f.FullName.Substring($logs.Length + 1)
            try {
                CopyVmLog -src $f.FullName -dst $dst
            } catch {
                Write-Host "VM logs: $($f.FullName) not copied: $_"
            }
        }
    }
    if (Test-Path -LiteralPath $destRoot) {
        Write-Host "VM logs collected in $destRoot"
    }
}

function CopyVmLog {
    param (
        [string]$src,
        [string]$dst
    )
    $srcLen = (Get-Item -LiteralPath $src).Length
    if (Test-Path -LiteralPath $dst) {
        $dstLen = (Get-Item -LiteralPath $dst).Length
        if ($srcLen -lt $dstLen -or -not (SameVmLogHead -a $src -b $dst -len $dstLen)) {
            $n = 1
            while (Test-Path -LiteralPath "$dst.$n") { $n++ }
            Move-Item -LiteralPath $dst -Destination "$dst.$n" -Force
        } elseif ($srcLen -eq $dstLen) {
            return
        }
    }
    $dir = Split-Path $dst -Parent
    if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
    # Shared-read open: after a failure the app's session is still running and the
    # VM holds the log open for writing, which fails File.Copy / Copy-Item with a
    # sharing violation.
    $in = [IO.File]::Open($src, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete)
    try {
        $out = [IO.File]::Create($dst)
        try { $in.CopyTo($out) } finally { $out.Close() }
    } finally {
        $in.Close()
    }
}

# True when the first min(512, len) bytes of both files match: the same log
# file (grown or unchanged) rather than a new launch's log under a reused name.
function SameVmLogHead {
    param (
        [string]$a,
        [string]$b,
        [long]$len
    )
    $n = [int][Math]::Min(512, $len)
    if ($n -le 0) { return $true }
    $ba = New-Object byte[] $n
    $bb = New-Object byte[] $n
    $fa = [IO.File]::Open($a, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete)
    try { $ra = $fa.Read($ba, 0, $n) } finally { $fa.Close() }
    $fb = [IO.File]::Open($b, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite)
    try { $rb = $fb.Read($bb, 0, $n) } finally { $fb.Close() }
    if ($ra -ne $rb) { return $false }
    for ($i = 0; $i -lt $ra; $i++) {
        if ($ba[$i] -ne $bb[$i]) { return $false }
    }
    return $true
}

# Start the SikuliX test for the app.
function StartTest {
    param (
        [string]$image,
        [string]$localLogsDir
    )
    if ([string]::IsNullOrWhiteSpace($localLogsDir)) {
        $localLogsDir = "$env:USERPROFILE\Desktop"
    }

    # Get the name string for the log file.
    $name = $image -replace '[/]', '_'

    # Clear any error before running the sikulix test.
    $Error.Clear()

    # turbo runs sikulix in a console hosted by Windows Terminal (the Windows 11 24H2
    # default terminal). Because Invoke-Expression runs turbo in this executor's own
    # console, turbo restores that Windows Terminal window - which HidePowerShellWindow
    # had minimized - and it pops up over the screen center, covering whatever the
    # sikulix test is trying to match and producing spurious FindFailed. It cannot be
    # suppressed at launch: GetConsoleWindow returns the hidden ConPTY window under
    # Windows Terminal (not the visible frame), a minimized/hidden window style is
    # ignored, and CreateNoWindow makes turbo exit 128 (which Invoke-AppTest.ps1 reads
    # as a failure). So keep launching with Invoke-Expression (so $LASTEXITCODE is
    # turbo's real exit code) and, for the duration of the test, keep the covering
    # console minimized from an in-process runspace. We minimize only the harness-owned Windows
    # Terminal windows - turbo's container console and this executor's PowerShell, identified by
    # their window titles - plus this executor's own console handle (the classic-conhost case
    # on Server 2019, where GetConsoleWindow does return the real window). App consoles
    # a test legitimately checks - e.g. apache's httpd window - are classic conhost; consoles a
    # test opens itself (a Start Menu Command Prompt, hosted by Windows Terminal on Win11) carry
    # neither title and are left visible. The remaining harness consoles
    # windows owned by the app, never Windows Terminal and never this executor's
    # console, so they are left alone. SW_SHOWMINNOACTIVE (7) minimizes without
    # activating another window, and already-minimized windows are skipped, so focus is
    # never stolen from the app the sikulix test drives with the keyboard.
    $consoleTypeDef = @'
using System;
using System.Runtime.InteropServices;
public class SikuliConsole {
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int n);
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, System.Text.StringBuilder s, int max);
    public static long ExecutorConsole() { return (long)GetConsoleWindow(); }
    private static void MinIfShown(IntPtr h) { if (IsWindowVisible(h) && !IsIconic(h)) ShowWindow(h, 7); }
    public static void MinimizeCovering(long executorConsole) {
        if (executorConsole != 0) MinIfShown(new IntPtr(executorConsole));
        EnumWindows(delegate(IntPtr h, IntPtr l) {
            if (IsWindowVisible(h) && !IsIconic(h)) {
                uint pid; GetWindowThreadProcessId(h, out pid);
                try {
                    var p = System.Diagnostics.Process.GetProcessById((int)pid);
                    if (p.ProcessName.ToLowerInvariant() == "windowsterminal") {
                        // Only the harness's own terminals: turbo's container console (titled
                        // with turbo.exe) and this executor's PowerShell (WindowsPowerShell in the title). A console the TEST
                        // opens (a Start Menu "Command Prompt" - winget, adobe_*, pandoc, ...)
                        // must stay visible so sikulix can read it.
                        var sb = new System.Text.StringBuilder(512); GetWindowText(h, sb, 512);
                        string title = sb.ToString().ToLowerInvariant();
                        if (title.Contains("turbo.exe") || title.Contains("windowspowershell")) ShowWindow(h, 7);
                    }
                } catch { }
            }
            return true;
        }, IntPtr.Zero);
    }
}
'@
    if (-not ([System.Management.Automation.PSTypeName]'SikuliConsole').Type) {
        Add-Type -TypeDefinition $consoleTypeDef
    }
    $executorConsole = [SikuliConsole]::ExecutorConsole()

    # Run the minimize loop in an in-process runspace (a background thread), NOT a
    # Start-Job: Start-Job launches a child powershell.exe, which under Windows Terminal
    # opens its OWN console window - adding to the covering it is meant to remove. A
    # runspace shares this process, so it spawns no console.
    $stopFlag = [hashtable]::Synchronized(@{ Stop = $false })
    $runspace = [runspacefactory]::CreateRunspace()
    $runspace.Open()
    $runspace.SessionStateProxy.SetVariable('executorConsole', $executorConsole)
    $runspace.SessionStateProxy.SetVariable('stopFlag', $stopFlag)
    $minimizer = [powershell]::Create()
    $minimizer.Runspace = $runspace
    [void]$minimizer.AddScript({
        while (-not $stopFlag.Stop) {
            [SikuliConsole]::MinimizeCovering($executorConsole)
            Start-Sleep -Milliseconds 300
        }
    })
    $asyncResult = $minimizer.BeginInvoke()

    $exitCode = 0
    try {
        # The sikulix launch should use java.exe instead of javaw.exe as we found that javaw takes focus when running the sikulix test scripts so key passes didn't get sent to the application.
        $command = "turbo run sikulixide --using=oracle/jre-x64 --offline --disable=spawnvm --isolate=merge-user --startup-file=javaw -- -jar @SYSDRIVE@\SikulixIDE\sikulixide-2.0.5.jar -r $($PSScriptRoot)\..\$name\test.sikuli -f $($localLogsDir)\$name-test.log"
        Invoke-Expression $command | Out-Host
        $exitCode = $LASTEXITCODE
    } finally {
        $stopFlag.Stop = $true
        try { $null = $minimizer.EndInvoke($asyncResult) } catch { }
        $minimizer.Dispose()
        $runspace.Close()
        $runspace.Dispose()
    }

    # The test is over: the last session's VM logs (or, on a failure, the
    # still-running session's) are collected now. See CollectVmLogs.
    try {
        CollectVmLogs -image $image
    } catch {
        Write-Host "VM logs: collection failed: $_"
    }

    return $exitCode

}

# Write a TEST-DONE-PASS or TEST-DONE-FAIL marker file on the desktop. The
# test runs with console windows minimized, so the marker is the visible
# signal for a person watching the desktop that the run has finished.
# PrepareTest removes stale markers at the start of each run.
function Write-TestDoneMarker {
    param (
        [string]$image,
        [int]$testResult
    )
    if ($testResult -eq 0) {
        "$image Pass at $(Get-Date -Format 'o')" | Set-Content "$env:USERPROFILE\Desktop\TEST-DONE-PASS"
    } else {
        "$image Fail (exit $testResult) at $(Get-Date -Format 'o')" | Set-Content "$env:USERPROFILE\Desktop\TEST-DONE-FAIL"
    }
}

# Most of the apps share the same testing procedure.
function StandardTest {
    param (
        [string]$image,
        [string]$using,
        [string]$isolate,
        [string]$extra,
        [bool]$shouldInstall = $true,
        [bool]$shouldTry = $true,
        [bool]$detached = $true,
        [string]$localLogsDir
    )

    PrepareTest -image $image -localLogsDir $localLogsDir -extra $extra
    PullTurboImages -image $image -using $using

    if ($shouldInstall) {
        InstallTurboApp -image $image -using $using -isolate $isolate -extra $extra
    }
    if ($shouldTry) {
    TryTurboApp -image $image -using $using -isolate $isolate -extra $extra -detached $detached
    }
    HidePowerShellWindow
    $TestResult = StartTest -image $image -localLogsDir $localLogsDir
    Write-TestDoneMarker -image $image -testResult $TestResult

    return $TestResult
}
