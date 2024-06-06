param (
    [string]$App,
    [string]$APIKey,
    [string]$ServerURL,
    [string]$AppVer,
    [string]$Publish,  # Accepting as string
    [string]$PushAPIKey,
    [string]$PushURL,
    [string]$PushVersion,
    [string]$LocalLogsDir
)
if (!$App) {
        $App = Read-Host -Prompt 'Enter App name'
    }
if (!$LocalLogsDir) {
        $LogsDir = New-Item -Path "$env:USERPROFILE\Desktop" -Name "Logs" -ItemType "directory" -Force
        $AppLogsDir = New-Item -Path $LogsDir -Name $App  -ItemType "directory" -Force       
        $FormattedDate = (get-date -displayhint DateTime) -replace ",", "-" -replace "/","-" -replace ":","-" -replace " ", "-"
        $LocalLogsDir = New-Item -Path "$AppLogsDir" -Name $FormattedDate -ItemType directory
    }


Start-Transcript -Path "$LocalLogsDir\TestPS.log"

if ($Publish -eq "true") {
    if (!$PushURL -or !$PushAPIKey) {
        Write-Host "publish = $Publish"
        Write-Host "-PushURL and -PushAPIKey parameters must be provided to publish the image."
        Exit 1 # Exit the current script
    }
}

# Path constants
$ScriptsDir = Join-Path $PSScriptRoot -ChildPath "Scripts"
$CommonDir = Join-Path $ScriptsDir -ChildPath "Common"
$AppDir = Join-Path $ScriptsDir -ChildPath $App

$Executor = "executor.ps1"
$AppLog = Join-Path $LocalLogsDir -ChildPath ($App + "-log.txt")
$PublishScript = "$PSScriptRoot\Publish.ps1"
Add-Type -AssemblyName System.Windows.Forms


# Function to display the Yes/No dialog box
function Show-Dialog {
param (
    [string]$message,
    [string]$title,
    [string]$buttons
)
    $form = New-Object System.Windows.Forms.Form
    $form.TopMost = $true

    If ($buttons -eq "YesNo") {
        $result = [System.Windows.Forms.MessageBox]::Show($form, $message, $title, [System.Windows.Forms.MessageBoxButtons]::YesNo)
        return $result
    }
    If ($buttons -eq "OK") {
            $result = [System.Windows.Forms.MessageBox]::Show($form, $message, $title, [System.Windows.Forms.MessageBoxButtons]::OK)
    }
    $form.Dispose()
}


try {
    powershell -executionpolicy bypass -file (Join-Path $AppDir -ChildPath $Executor) -LocalLogsDir $LocalLogsDir

    # Read the result of the test log file for error
    $testLogFile = "$LocalLogsDir\$App-test.log"
    $fileContent = Get-Content $testLogFile
    $filteredContent = $fileContent | Where-Object { $_ -notmatch "RobotDesktop" } # Filter out lines containing "RobotDesktop"
    $filteredContent = $filteredContent | Where-Object { $_ -notmatch "Mouse: not useable" } # Filter out lines containing "RobotDesktop"
    $ErrorResultLine = $filteredContent | Select-String "error"  # Search for the line containing "[error]"
   
    if ($ErrorResultLine -or (-not $fileContent)) {
        $ExitCode = 1 # Error or Fail
        Write-Host "Test Result = Fail"
        $message = "Test result: Fail!`n`nError: $ErrorResultLine`nSee log files in:`n$LocalLogsDir`n"
    } else {
        $ExitCode = 0 # Success
        Write-Host "Test Result = Success"
        $message = "Test result: Success!`n`nSee log files in:`n$LocalLogsDir`n`n"
    }
}
finally {
    
    If ($ExitCode -eq 0) {
        If ($Publish -eq "true") {
            $message = $message + "Would you like to Publish the image?"
            $response = Show-Dialog -message $message -title "Successful" -buttons "YesNo"
            if ($response -eq [System.Windows.Forms.DialogResult]::Yes) {
                powershell -ExecutionPolicy bypass -File $PublishScript -App $App -ServerURL $PushURL -APIKey $PushAPIKey -AppVer $PushVersion -LocalLogsDir $LocalLogsDir
            } else {
                Write-Output "You selected No. Skipping publish."
            }
        } else {
            Write-Output "Publish is set to $Publish. Skipping publish."
            Show-Dialog -message $message -title "Successful!" -buttons "OK"
        }
    } else {
        Write-Output $message
        Show-Dialog -message $message -title "Failed!" -buttons "OK"
    }
}

return $ExitCode