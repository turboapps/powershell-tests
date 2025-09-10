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
    turbo pull /xvm
    turbo pull base
    turbo pull sikulix/sikulixide
    turbo pull oracle/jre-x64
}

# Pull Turbo images (app image and images in the `--using` list).
function PullTurboImages {
    param (
        [string]$image,
        [string]$using
    )

    turbo pull $image

    if (-not [string]::IsNullOrWhiteSpace($using)) {
        $using.Split(",") | ForEach-Object {
            turbo pull $_.Trim()
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

    $command = "turbo installi $image --offline --enable=disablefontpreload,usedllinjection"

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

    $command = "try $image --name=test --enable=disablefontpreload,usedllinjection"

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

    $command = "run $image --enable=disablefontpreload,usedllinjection"

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
    }
"@

    # Constant for minimizing the window.
    $SW_MINIMIZE = 6

    # Get the window handle for the console.
    $consoleHandle = [WindowHandler]::GetConsoleWindow()

    # Minimize the window.
    [WindowHandler]::ShowWindow($consoleHandle, $SW_MINIMIZE)

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

    # The sikulix launch should use java.exe instead of javaw.exe as we found that javaw takes focus when running the sikulix test scripts so key passes didn't get sent to the application.
    $command = "turbo run sikulixide --using=oracle/jre-x64 --offline --disable=spawnvm --isolate=merge-user --startup-file=java -- -jar @SYSDRIVE@\SikulixIDE\sikulixide-2.0.5.jar -r $($PSScriptRoot)\..\$name\test.sikuli -f $($localLogsDir)\$name-test.log"
    Invoke-Expression $command    

    return $LASTEXITCODE
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

    return $TestResult
}
