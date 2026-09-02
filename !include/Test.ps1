$NewLine = [System.Environment]::NewLine

# Clean the environment for tests, pull test related images and login to a Turbo Server.
# Note: this funtion will remove all the Turbo sessions, unregister all the apps installed by Turbo and reset Turbo Client configurations.
function PrepareTest {
    param (
        [string]$image,
        [string]$secretsFile,
        [string]$localLogsDir
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

    PrepareTest -image $image -localLogsDir $localLogsDir
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
