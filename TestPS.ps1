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
# Create a Logs folder on the desktop to store the test logs
if (!$LocalLogsDir) {
        $LogsDir = New-Item -Path "$env:USERPROFILE\Desktop" -Name "Logs" -ItemType "directory" -Force
        $AppLogsDir = New-Item -Path $LogsDir -Name $App  -ItemType "directory" -Force       
        $FormattedDate = (get-date -displayhint DateTime) -replace ",", "-" -replace "/","-" -replace ":","-" -replace " ", "-"
        $LocalLogsDir = New-Item -Path "$AppLogsDir" -Name $FormattedDate -ItemType directory
    }

# Create a transcript of this script
Start-Transcript -Path "$LocalLogsDir\TestPS.log"

# The script should exit if $Publish is "true" but the required parameters were not passed
# If this script was launched by the HTA, this should not be possible
if ($Publish -eq "true") {
    if (!$PushURL -or !$PushAPIKey -or !$PushVersion) {
        Write-Host "publish = $Publish"
        Write-Host "-PushURL and -PushAPIKey and $PushVersion parameters must be provided to publish the image."
        Exit 1 # Exit the current script
    }
}

# Path constants
$AppDir = Join-Path $PSScriptRoot -ChildPath $App
$Executor = "executor.ps1"
$AppLog = Join-Path $LocalLogsDir -ChildPath ($App + "-log.txt")
$PublishScript = "$PSScriptRoot\Publish.ps1"
Add-Type -AssemblyName System.Windows.Forms


# Function to display the dialog box with the test result message
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
    # Run the Executor.ps1 script from the folder for the selected application to test
    powershell -executionpolicy bypass -file (Join-Path $AppDir -ChildPath $Executor) -LocalLogsDir $LocalLogsDir

    # Read the result of the sikulix test log file for error
    $testLogFile = "$LocalLogsDir\$App-test.log"
    $fileContent = Get-Content $testLogFile

    # Filter out error lines that may result in a false negative failure of the sikulix test
    $filteredContent = $fileContent | Where-Object { $_ -notmatch "RobotDesktop" }
    $filteredContent = $filteredContent | Where-Object { $_ -notmatch "Mouse: not useable" }
    $ErrorResultLine = $filteredContent | Select-String "error"  # Search for a line containing "error"
   
    # If an error line was found in the sikulix test log consider the test a failure
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
        # If the test was a success and SPublish is true, prompt for a confirmation to publish 
        If ($Publish -eq "true") {
            $message = $message + "Would you like to Publish the image?"
            $response = Show-Dialog -message $message -title "Successful" -buttons "YesNo"
            # Run the Publish.ps1 script if user confirms the publish
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