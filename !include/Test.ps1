$NewLine = [System.Environment]::NewLine

# Turbo Server sign-in (Connect-TurboServer).
. "$PSScriptRoot\HubAuth.ps1"

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
    $clientId = $secrets | Where-Object { $_.Key -eq "ClientId" } | Select-Object -ExpandProperty Value
    $clientSecret = $secrets | Where-Object { $_.Key -eq "ClientSecret" } | Select-Object -ExpandProperty Value

    # Stop all Turbo sessions.
    turbo stop -a

    # Remove all Turbo sessions.
    turbo rm -a

    # Turbo VM logs from a previous run (see CollectVmLogs), for the same reason
    # as the step frames. Removed only now that no session is left: a file there
    # can be a hard link to a log a still-running container held open, and such
    # a link cannot be deleted while the VM has it open.
    Remove-Item "$env:USERPROFILE\Desktop\$name-vm-logs" -Recurse -Force -ErrorAction SilentlyContinue

    # Uninstall all the apps installed by Turbo Client.
    turbo uninstalli -a

    # Reset client config
    turbo config --reset

    # Pull the base and xvm images from hub.turbo.net
    turbo pull /xvm --format=json
    turbo pull base --format=json

    # Point to the specified Turbo Server and log in.
    if ([string]::IsNullOrWhiteSpace($domain)) {
        Write-Host "Domain not found in secrets.txt"
        Exit 1
    }

    # A credential is required except for https://turbo.net: an APIKey (a server before 2.0), or a
    # registered OAuth client of a 2.0 server, as ClientId/ClientSecret entries or an APIKey of the
    # form client:<id>:<secret>. Connect-TurboServer (HubAuth.ps1) signs in whichever client this is.
    $credential = $apiKey
    if (-not [string]::IsNullOrWhiteSpace($clientId) -and -not [string]::IsNullOrWhiteSpace($clientSecret)) {
        $credential = "client:${clientId}:$clientSecret"
    }
    if (-not [string]::IsNullOrWhiteSpace($credential)) {
        # Fatal: the client would otherwise go on pulling from whatever server it is still pointed at
        # (turbo.net when `turbo config --domain` could not reach $domain) and a pass would be for
        # images that never came from $domain.
        if (-not (Connect-TurboServer -Server $domain -Credential $credential)) {
            Write-Host "Could not sign in to $domain; is it reachable from this machine?"
            Exit 1
        }
    } else {
        turbo config --domain $domain
        Write-Host "No APIKey or ClientId/ClientSecret in secrets.txt; not signing in"
    }

    # Pull test related images. There won't be test under full isolation, so no need to pull clean.
    turbo pull sikulix/sikulixide --format=json
    turbo pull oracle/jre-x64 --format=json

    # From here on every container's VM logs are captured as they appear,
    # including those of `try` sessions the client deletes when they end. See
    # Start-VmLogLinker.
    try {
        Start-VmLogLinker -image $image
    } catch {
        Write-Host "VM logs: live capture not started: $_"
    }
}

# Pull Turbo images (app image and images in the `--using` list).
function PullTurboImages {
    param (
        [string]$image,
        [string]$using
    )

    PullTurboImage -image $image

    if (-not [string]::IsNullOrWhiteSpace($using)) {
        $using.Split(",") | ForEach-Object {
            PullTurboImage -image $_.Trim()
        }
    }
}

# Pull one image, retrying a failed pull.
#
# A pull that fails part-way leaves a .downloadpart behind and gives up with
# "The connection may have timed out" (exit -1). The test's own launch then
# resumes that download inside the test's first wait, which no budget can cover
# for a multi-GB image: App Tests run 35935367711 lost the connection twice
# pulling vsbuildtools-arm64 (4.6 GB), and nodejs-arm64 then failed at
# focus_console with 2.6 GB still to fetch. Pulling again here resumes the
# .downloadpart rather than starting over.
function PullTurboImage {
    param (
        [string]$image,
        [int]$attempts = 5
    )

    # $global: because the CI harness (applab Invoke-AppTest.ps1) assigns
    # $LASTEXITCODE in its own scope before calling the executor, and that copy
    # shadows the automatic variable here: a bare $LASTEXITCODE reads 0 no matter
    # what turbo returned.
    for ($attempt = 1; $attempt -le $attempts; $attempt++) {
        turbo pull $image --format=json
        if ($global:LASTEXITCODE -eq 0) { return }
        Write-Host "turbo pull $image failed with exit code $global:LASTEXITCODE (attempt $attempt of $attempts)"
    }
    Write-Warning "turbo pull $image failed $attempts times; the test's launch will have to download it"
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

    # `try` removes the session - sandbox and VM logs included - the moment it
    # ends, so on a diagnostic run (--diagnostic in -extra) the same launch is
    # made with `run`: the session then persists until the next PrepareTest's
    # `turbo rm -a`, and CollectVmLogs / util.check_running() can copy its logs
    # after it has stopped. Everything else about the command is identical.
    # util.try_verb() makes the same choice for launches a test issues itself.
    # A `try` session's logs are not lost either way: Start-VmLogLinker links
    # them out as they are created (see CollectVmLogs).
    $verb = if ($extra -match '(^|\s)--diagnostic(\s|$)') { "run" } else { "try" }
    $command = "$verb $image --name=test --enable=disablefontpreload,usedllinjection,cachefileinfo --network=test --disable-proxy-resolve-via-proxy"

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

# Configure Windows Defender settings.
# Best effort: the test does not depend on these settings, and on a freshly
# booted VM the Defender WMI provider can still be starting and answer
# 0x800106ba. Under a caller's $ErrorActionPreference = 'Stop' (the CI
# harness) that error used to abort the executor before SikuliX ever started.
# Retry every 30 s for up to ~300 s, then warn and carry on.
function ConfigureDefender {

    $deadline = (Get-Date).AddSeconds(300)
    while ($true) {
        try {
            # Disable Cloud-delivered protection
            Set-MpPreference -MAPSReporting Disabled -ErrorAction Stop
            # Disable Automatic sample submission
            Set-MpPreference -SubmitSamplesConsent NeverSend -ErrorAction Stop
            return
        } catch {
            if ((Get-Date) -ge $deadline) {
                Write-Warning "ConfigureDefender: giving up, Defender settings left unchanged: $($_.Exception.Message)"
                return
            }
            Write-Warning "ConfigureDefender: Defender not ready ($($_.Exception.Message)); retrying in 30 s"
            Start-Sleep -Seconds 30
        }
    }

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
# Every container writes its VM logs to <sandbox>\logs: xcstream_0x<pid>.txt
# (the process's command line and console streams) and xcnetwork_0x<pid>.txt
# always, and xclog_0x<pid>.txt (the VM diagnostic log) when it was started with
# --diagnostic (the CI harness's vm_diagnostics run passes it in -extra). The
# whole folder is collected, whatever it holds, so a log a later VM adds is
# picked up without a harness change.
#
# The client deletes and recreates that folder every time the same container
# starts again, and deletes a `try` session's sandbox - logs included - the
# moment the session ends. So the logs are captured while they exist, in two
# ways, neither of which polls:
#
#  - Start-VmLogLinker (from PrepareTest) hard-links each log file into the
#    Desktop folder as soon as the file is created. The link is the same file,
#    not a copy: it sees every later write, costs nothing while the test runs,
#    and outlives the client's delete of the sandbox, so a `try` launch's logs
#    survive complete even though the session is gone by the end of the test.
#  - CollectVmLogs copies whatever is still in a sandbox, after the sikulix
#    test returned (which also covers a failure, where the app's session is
#    usually still running with its dialogs on screen), and
#    util.check_running() does the same after a session ended mid-test. This
#    is the fallback for a file the linker missed or could not link.
#
# The SikuliX harness's own container is left out (CollectVmLogs removes what
# the linker took from it): see IsHarnessSandbox.
#
# Layout: <Desktop>\<app>-vm-logs\<container id>\<logs tree>. The CI harness
# (applab Invoke-AppTest.ps1) stages that folder as the <app>-vm-logs artifact.
# A copy is skipped when the destination already is that file (a link), is
# overwritten when the source is the same file grown, and is kept as
# <name>.1, .2, ... when a different file has reappeared under the same name
# (pid reuse across launches); the linker applies the same rotation.
# util.collect_vm_logs() implements the same rule. Best-effort: never changes
# the test result.
# The sandbox root the client is using. `turbo config --reset` (PrepareTest)
# leaves the default location; honour a relocated storage path anyway when the
# client reports one.
function GetSandboxRoot {
    $root = "$env:LOCALAPPDATA\Turbo\Containers\sandboxes"
    try {
        $cfg = (turbo config --format=json 2>$null | Out-String | ConvertFrom-Json)[0].result.configuration
        if ($cfg.containerStoragePath) { $root = [Environment]::ExpandEnvironmentVariables($cfg.containerStoragePath) }
    } catch { }
    return $root
}

function Initialize-VmLogLinker {
    if (([System.Management.Automation.PSTypeName]'VmLogLinker').Type) { return }
    $typeDef = @'
using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;

public static class VmLogLinker {
    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern bool CreateHardLink(string newName, string existing, IntPtr security);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
    static extern IntPtr CreateFile(string name, uint access, uint share, IntPtr security, uint disposition, uint flags, IntPtr template);

    [DllImport("kernel32.dll", SetLastError = true)]
    static extern bool GetFileInformationByHandle(IntPtr h, out FileInfoByHandle info);

    [DllImport("kernel32.dll")]
    static extern bool CloseHandle(IntPtr h);

    [StructLayout(LayoutKind.Sequential)]
    struct FileInfoByHandle {
        public uint Attributes;
        public System.Runtime.InteropServices.ComTypes.FILETIME Created, Accessed, Written;
        public uint VolumeSerial, SizeHigh, SizeLow, Links, IndexHigh, IndexLow;
    }

    static readonly object Gate = new object();
    static FileSystemWatcher watcher;
    static string root;
    static string dest;
    static int generation;
    static int linked;
    static int failed;
    static string lastError;
    static readonly Dictionary<string, int> linkedBySandbox = new Dictionary<string, int>(StringComparer.OrdinalIgnoreCase);

    public static int Linked { get { return linked; } }
    // Files linked out of one sandbox (by container id), so a caller that
    // drops a container's logs can drop them from the count too.
    public static int LinkedFrom(string sandboxId) {
        lock (Gate) { int n; return linkedBySandbox.TryGetValue(sandboxId, out n) ? n : 0; }
    }
    public static int Failed { get { return failed; } }
    public static string LastError { get { return lastError; } }

    // One watcher, on the sandbox root - a directory the client never deletes.
    // No handle is ever held on a sandbox or its logs folder: the client
    // deletes and recreates logs on every container start, and an open handle
    // would leave the old folder delete-pending and fail the recreate.
    // Before the client has created the root, its nearest existing parent is
    // watched instead.
    //
    // Watching recursively means every file the app creates in its sandbox is
    // reported too, and the kernel drops notifications if its buffer fills
    // before the next read. So the handler does nothing but a string test and
    // queues the real work, which keeps the buffer drained; a larger buffer
    // (allowed on a local volume) gives headroom; and an overflow triggers a
    // sweep that links whatever is there. FileSystemWatcher.Filter would not
    // help: it is applied after the kernel buffer, not in it.
    public static void Start(string sandboxRoot, string destRoot) {
        lock (Gate) {
            StopLocked();
            root = Path.GetFullPath(sandboxRoot).TrimEnd('\\') + "\\";
            dest = Path.GetFullPath(destRoot);
            linked = 0;
            linkedBySandbox.Clear();
            failed = 0;
            lastError = null;
            ArmLocked();
        }
        Sweep();
    }

    public static void Stop() {
        lock (Gate) StopLocked();
    }

    static void StopLocked() {
        generation++;
        var w = watcher;
        watcher = null;
        if (w != null) {
            w.EnableRaisingEvents = false;
            w.Dispose();
        }
    }

    static void ArmLocked() {
        int gen = ++generation;
        string watch = root.TrimEnd('\\');
        while (!Directory.Exists(watch)) {
            string parent = Path.GetDirectoryName(watch);
            if (string.IsNullOrEmpty(parent)) throw new DirectoryNotFoundException(root);
            watch = parent;
        }
        var w = new FileSystemWatcher(watch);
        w.IncludeSubdirectories = true;
        w.NotifyFilter = NotifyFilters.FileName | NotifyFilters.DirectoryName;
        w.InternalBufferSize = 256 * 1024;
        w.Created += delegate(object s, FileSystemEventArgs e) { Notified(e.FullPath); };
        w.Renamed += delegate(object s, RenamedEventArgs e) { Notified(e.FullPath); };
        w.Error += delegate(object s, ErrorEventArgs e) { Errored(gen, e.GetException()); };
        w.EnableRaisingEvents = true;
        watcher = w;
    }

    static void Notified(string path) {
        if (IsLogsPath(path)) ThreadPool.QueueUserWorkItem(delegate { Consider(path); });
    }

    static void Errored(int gen, Exception error) {
        string message = error == null ? "unknown" : error.Message;
        if (!(error is InternalBufferOverflowException)) {
            // Anything else may have stopped the watcher: replace it.
            lock (Gate) {
                if (gen != generation) return;
                StopLocked();
                try { ArmLocked(); } catch (Exception e) { Fail("re-arm: " + e.Message); }
            }
        }
        lastError = "watcher: " + message;
        ThreadPool.QueueUserWorkItem(delegate { Sweep(); });
    }

    static void Fail(string message) {
        Interlocked.Increment(ref failed);
        lastError = message;
    }

    // <root><id>\logs or anything below it.
    static bool IsLogsPath(string path) {
        string r = root;
        if (r == null || path.Length <= r.Length || !path.StartsWith(r, StringComparison.OrdinalIgnoreCase)) return false;
        int sep = path.IndexOf('\\', r.Length);
        if (sep < 0) return false;
        int end = path.IndexOf('\\', sep + 1);
        string second = end < 0 ? path.Substring(sep + 1) : path.Substring(sep + 1, end - sep - 1);
        return string.Equals(second, "logs", StringComparison.OrdinalIgnoreCase);
    }

    // True when both paths name the same file (one is a hard link of the other).
    public static bool SameFile(string a, string b) {
        FileInfoByHandle ia, ib;
        if (!Identify(a, out ia) || !Identify(b, out ib)) return false;
        return ia.VolumeSerial == ib.VolumeSerial && ia.IndexHigh == ib.IndexHigh && ia.IndexLow == ib.IndexLow;
    }

    static bool Identify(string path, out FileInfoByHandle info) {
        info = new FileInfoByHandle();
        // No data access, all sharing: never conflicts with the VM's open handle.
        IntPtr h = CreateFile(path, 0, 7, IntPtr.Zero, 3, 0x02000000, IntPtr.Zero);
        if (h == new IntPtr(-1)) return false;
        try { return GetFileInformationByHandle(h, out info); } finally { CloseHandle(h); }
    }

    static void Sweep() {
        try {
            string r = root;
            if (r == null || !Directory.Exists(r)) return;
            foreach (string sandbox in Directory.GetDirectories(r)) {
                string logs = Path.Combine(sandbox, "logs");
                if (Directory.Exists(logs)) Consider(logs);
            }
        } catch (Exception e) {
            Fail("sweep: " + e.Message);
        }
    }

    static void Consider(string path) {
        try {
            if (!IsLogsPath(path)) return;
            if (Directory.Exists(path)) {
                // A logs folder (or a folder below it) that appeared whole: its
                // files raise no notification of their own.
                foreach (string f in Directory.GetFiles(path, "*", SearchOption.AllDirectories)) Consider(f);
                return;
            }
            string[] parts = path.Substring(root.Length).Split('\\');
            if (parts.Length < 3) return;
            Link(parts[0], path, Path.Combine(dest, parts[0], string.Join("\\", parts, 2, parts.Length - 2)));
        } catch (Exception e) {
            Fail(path + ": " + e.Message);
        }
    }

    static void Link(string sandboxId, string src, string dst) {
        lock (Gate) {
            if (File.Exists(dst)) {
                if (SameFile(src, dst)) return;
                if (IsCopyOf(dst, src)) {
                    // A fallback copy (CollectVmLogs, check_running) of this
                    // same log: the link supersedes it.
                    File.Delete(dst);
                } else {
                    // A different file under a name already taken: an earlier
                    // launch's log (pid reuse). Keep it, as CollectVmLogs does.
                    int n = 1;
                    while (File.Exists(dst + "." + n)) n++;
                    File.Move(dst, dst + "." + n);
                }
            }
            Directory.CreateDirectory(Path.GetDirectoryName(dst));
            if (CreateHardLink(dst, src, IntPtr.Zero)) {
                linked++;
                int n;
                linkedBySandbox.TryGetValue(sandboxId, out n);
                linkedBySandbox[sandboxId] = n + 1;
            } else {
                int error = Marshal.GetLastWin32Error();
                // 2/3: the file was already gone again - nothing to keep.
                if (error != 2 && error != 3) Fail("link " + src + ": Win32 error " + error);
            }
        }
    }

    // CollectVmLogs' rule for "the same file, grown": the copy is no longer
    // than the source and their first bytes match. Lengths come from the open
    // files, not the directory: a hard link's directory entry is refreshed
    // lazily and can report a stale size.
    static bool IsCopyOf(string copy, string source) {
        try {
            using (var c = new FileStream(copy, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete))
            using (var s = new FileStream(source, FileMode.Open, FileAccess.Read, FileShare.ReadWrite | FileShare.Delete)) {
                if (c.Length > s.Length) return false;
                int n = (int)Math.Min(512, c.Length);
                var bc = new byte[n];
                var bs = new byte[n];
                if (c.Read(bc, 0, n) != n || s.Read(bs, 0, n) != n) return false;
                for (int i = 0; i < n; i++) if (bc[i] != bs[i]) return false;
                return true;
            }
        } catch (Exception) {
            return false;
        }
    }
}
'@
    Add-Type -TypeDefinition $typeDef
}

# Start capturing every container's VM logs as they are created (see above).
# The watcher lives in this process - the executor's, which on CI is
# Invoke-AppTest.ps1's - until it exits or the next PrepareTest restarts it.
# A hard link needs the Desktop and the sandbox root on one volume; where they
# are not, every link fails and CollectVmLogs' copies are all there is.
function Start-VmLogLinker {
    param (
        [string]$image
    )
    $name = $image -replace '[/]', '_'
    Initialize-VmLogLinker
    $root = GetSandboxRoot
    [VmLogLinker]::Start($root, "$env:USERPROFILE\Desktop\$name-vm-logs")
    Write-Host "VM logs: capturing every container's logs under $root as they are created"
}

function CollectVmLogs {
    param (
        [string]$image
    )
    $name = $image -replace '[/]', '_'
    $destRoot = "$env:USERPROFILE\Desktop\$name-vm-logs"

    # The copies below do not depend on the linker: if its type cannot be
    # loaded they still run, they just cannot recognise a link (see CopyVmLog).
    $linker = $false
    try {
        Initialize-VmLogLinker
        $linker = $true
    } catch {
        Write-Host "VM logs: live capture unavailable: $_"
    }

    $root = GetSandboxRoot
    $harnessLinked = 0
    foreach ($sb in @(if (Test-Path -LiteralPath $root) { Get-ChildItem -LiteralPath $root -Directory -ErrorAction SilentlyContinue })) {
        # The test harness's own container (StartTest's `turbo run sikulixide`)
        # is not the app under test: its only log is the fixed java command
        # line, and SikuliX's output is the test log. Drop it, including what
        # the linker already captured from it (and from the linker's count).
        if (IsHarnessSandbox -sandbox $sb.FullName) {
            if ($linker) { $harnessLinked += [VmLogLinker]::LinkedFrom($sb.Name) }
            $harnessDst = Join-Path $destRoot $sb.Name
            if (Test-Path -LiteralPath $harnessDst) {
                Remove-Item -LiteralPath $harnessDst -Recurse -Force -ErrorAction SilentlyContinue
            }
            continue
        }
        $logs = Join-Path $sb.FullName 'logs'
        if (-not (Test-Path -LiteralPath $logs)) { continue }
        foreach ($f in @(Get-ChildItem -LiteralPath $logs -File -Recurse -ErrorAction SilentlyContinue)) {
            $dst = Join-Path (Join-Path $destRoot $sb.Name) $f.FullName.Substring($logs.Length + 1)
            try {
                CopyVmLog -src $f.FullName -dst $dst
            } catch {
                Write-Host "VM logs: $($f.FullName) not copied: $_"
            }
        }
    }
    if ($linker) {
        $captured = [VmLogLinker]::Linked - $harnessLinked
        if ($captured -gt 0 -or [VmLogLinker]::Failed -gt 0) {
            $line = "VM logs: $captured file(s) captured as created"
            if ([VmLogLinker]::Failed -gt 0) { $line += ", $([VmLogLinker]::Failed) capture failure(s) (last: $([VmLogLinker]::LastError))" }
            Write-Host $line
        }
    }
    if (Test-Path -LiteralPath $destRoot) {
        Write-Host "VM logs collected in $destRoot"
    }
}

# True when the sandbox is the SikuliX harness's container: its meta.json lists
# the images it was started from, resolved ("inputImages", e.g.
# "sikulix/sikulixide", "oracle/jre-x64", possibly with :tag or #hash).
# Unreadable or missing metadata counts as not the harness, so an app container
# is never dropped by mistake.
function IsHarnessSandbox {
    param (
        [string]$sandbox
    )
    try {
        $meta = Get-Content -LiteralPath (Join-Path $sandbox 'meta.json') -Raw -ErrorAction Stop | ConvertFrom-Json
        foreach ($img in @($meta.inputImages)) {
            $leaf = (($img -split '[:#]')[0] -split '/')[-1]
            if ($leaf -ieq 'sikulixide') { return $true }
        }
    } catch { }
    return $false
}

function CopyVmLog {
    param (
        [string]$src,
        [string]$dst
    )
    $srcLen = (Get-Item -LiteralPath $src).Length
    if (Test-Path -LiteralPath $dst) {
        # Already captured: the destination is a hard link to this very file
        # (Start-VmLogLinker).
        $same = $false
        try { $same = [VmLogLinker]::SameFile($src, $dst) } catch { }
        if ($same) { return }
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
    #
    # Never written in place: the copy goes to a side file that then replaces
    # $dst. Should $dst be a link to $src that SameFile failed to recognise, the
    # replace drops that name (or, while the VM holds the log open without
    # delete sharing, fails and leaves the link) - writing through it would
    # truncate the log itself.
    $tmp = "$dst.partial"
    try {
        $in = [IO.File]::Open($src, [IO.FileMode]::Open, [IO.FileAccess]::Read, [IO.FileShare]::ReadWrite -bor [IO.FileShare]::Delete)
        try {
            $out = [IO.File]::Create($tmp)
            try { $in.CopyTo($out) } finally { $out.Close() }
        } finally {
            $in.Close()
        }
        if (Test-Path -LiteralPath $dst) { [IO.File]::Delete($dst) }
        [IO.File]::Move($tmp, $dst)
    } finally {
        if (Test-Path -LiteralPath $tmp) { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue }
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
        # $global: for the reason given in PullTurboImages: on CI a bare
        # $LASTEXITCODE reads Invoke-AppTest.ps1's own copy, which is always 0.
        $exitCode = $global:LASTEXITCODE
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

    # Written here rather than by StandardTest so that the executors which call
    # StartTest directly get a marker too.
    Write-TestDoneMarker -image $image -exitCode $exitCode -logFile "$localLogsDir\$name-test.log"

    return $exitCode

}

# Write a TEST-DONE-PASS or TEST-DONE-FAIL marker file on the desktop. The
# test runs with console windows minimized, so the marker is the visible
# signal for a person watching the desktop that the run has finished.
# PrepareTest removes stale markers at the start of each run.
#
# The verdict is the one Invoke-AppTest.ps1 reaches from the same evidence: a
# missing test log, a non-zero sikulix exit code, or any line of the test log
# containing "error" (SikuliX's "[error] script [ test ] stopped with error")
# is a failure. What the marker cannot see is the CI harness's own crash-dump
# gate, which runs after the executor returns and can still fail a run whose
# script passed.
function Write-TestDoneMarker {
    param (
        [string]$image,
        [int]$exitCode,
        [string]$logFile
    )
    $reason = $null
    if (-not (Test-Path $logFile)) {
        $reason = "no test log at $logFile"
    } elseif ($exitCode -ne 0) {
        $reason = "sikulix exit $exitCode"
    } else {
        $errorLine = Select-String -Path $logFile -Pattern "error" -SimpleMatch | Select-Object -First 1
        if ($errorLine) {
            $reason = "test log: $($errorLine.Line.Trim())"
        }
    }
    if ($reason) {
        "$image Fail ($reason) at $(Get-Date -Format 'o')" | Set-Content "$env:USERPROFILE\Desktop\TEST-DONE-FAIL"
        Write-Host "Test done marker: TEST-DONE-FAIL ($reason)"
    } else {
        "$image Pass at $(Get-Date -Format 'o')" | Set-Content "$env:USERPROFILE\Desktop\TEST-DONE-PASS"
        Write-Host "Test done marker: TEST-DONE-PASS (sikulix exit 0, no error in the test log)"
    }
}

# Most of the apps share the same testing procedure.
function StandardTest {
    param (
        [string]$image,
        [string]$app,
        [string]$using,
        [string]$isolate,
        [string]$extra,
        [bool]$shouldInstall = $true,
        [bool]$shouldTry = $true,
        [bool]$detached = $true,
        [string]$localLogsDir,
        [string]$testExtra
    )

    # extra.txt (util.read_extra()) carries the flags for launches the test
    # issues itself. That is -extra as the CI harness passed it; an executor that
    # decorates -extra with launch-specific additions (--startup-file, app
    # arguments after --) passes the undecorated value as -testExtra so those
    # do not end up on the test's own command lines.
    $forTest = if ($PSBoundParameters.ContainsKey('testExtra')) { $testExtra } else { $extra }

    # -image names the test: it selects the test.sikuli that runs and the
    # <name>-test.log / -executor.log / -steps / -vm-logs the CI harness reads
    # back (Invoke-AppTest.ps1 looks for <app>-test.log under the job's app
    # name). A test that exercises one product through another's front end -
    # microsoft/vsbuildtools compiling a native addon at a nodejs prompt -
    # passes that front end as -app, so only the container launch uses it.
    # Without -app the two are the same image, as they are for most tests.
    $launch = if ([string]::IsNullOrWhiteSpace($app)) { $image } else { $app }

    PrepareTest -image $image -localLogsDir $localLogsDir -extra $forTest
    PullTurboImages -image $launch -using $using

    if ($shouldInstall) {
        InstallTurboApp -image $launch -using $using -isolate $isolate -extra $extra
    }
    if ($shouldTry) {
    TryTurboApp -image $launch -using $using -isolate $isolate -extra $extra -detached $detached
    }
    HidePowerShellWindow
    $TestResult = StartTest -image $image -localLogsDir $localLogsDir

    return $TestResult
}
