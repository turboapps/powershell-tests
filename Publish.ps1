param (
    [string]$App,
    [string]$APIKey,
    [string]$ServerURL,
    [string]$AppVer,
    [string]$LocalLogsDir

)
if (!$App) {
        $App = Read-Host -Prompt 'Enter App name'
    }
if (!$LocalLogsDir) {
        $LogsDir = Join-Path $PSScriptRoot -ChildPath "Logs"
        $AppLogsDir = Join-Path $LogsDir -ChildPath $App
        if (!(Test-Path $LogsDir -PathType Container)) {New-Item -ItemType Directory -Path $LogsDir} 
        if (!(Test-Path $AppLogsDir -PathType Container)) {New-Item -ItemType Directory -Path $AppLogsDir}        
        $FormattedDate = (get-date -displayhint DateTime) -replace ",", "-" -replace "/","-" -replace ":","-" -replace " ", "-"
        $LocalLogsDir = New-Item -Path "$AppLogsDir" -Name $FormattedDate -ItemType directory
    }

# Set variables
$NewLine = "`r`n"  #  Adds a blank line to the Log file
$LogFile = "$LocalLogsDir\!Publish.log"  # Set path of log file

###############
## Functions ##
###############

# WriteLog - writes string message parameter to log file and console.
Function WriteLog([String]$message) {
    Write-Host "$message"
    $timestamp = Get-Date -Format o | foreach {$_ -replace ":", "."}
    ("$timestamp $message").replace($NewLine,"") | Out-File -FilePath $LogFile -Append # Strip new lines from message then output to log
}

# Compare the current Turbo Hub Version to the latest available download version.
# Exits the script if Hub is the same or newer.
function Compare-Versions($Version1, $Version2) {
    # If the version is null then set to 0.0
    if ($Version1 -eq $null) {$Version1 = "0.0"}
    if ($Version2 -eq $null) {$Version2 = "0.0"}
    # If the version doesn't have a decimal add .0 to it
    if ($Version1 -notmatch "\.") {$Version1 += ".0"}  
    if ($Version2 -notmatch "\.") {$Version2 += ".0"}  

    If ([Version]$Version1 -lt [Version]$Version2) {
         Return 1
    } Else {
         Return 0
    }
}

# Get Current Hub Version of application
Function GetCurrentHubVersion($App,$APIKey,$ServerURL) {
    # Split the repo parts into owner and name values
    $repoOwner, $repoName = $App -split "_"
    WriteLog "Getting the current $App version from $ServerURL"
    
    # Get token from API Key
    $headers = @{}
    $headers.Add("X-Turbo-Api-Key", $APIKey)
    $reqUrl = $ServerURL + '/0.1/api-keys/login'
    $response = Invoke-RestMethod -Uri $reqUrl -Method Get -Headers $headers  

    # Get all repos from Hub
    $headers = @{}
    $headers.Add("X-Turbo-Ticket", $response)
    $headers.Add("X-Turbo-Api-Id", "turbo.net")
    $headers.Add("X-Turbo-Api-Version", "1")

    # Get the revisions array for the repo
    $reqUrl = $ServerURL + '/io/_hub/repo/' + $repoOwner + '/' + $repoName + '/revisions?withTags'
    $response = Invoke-RestMethod -Uri $reqUrl -Method Get -Headers $headers  

    # Get the first imageID from the repo
    if ($response.imageid.count -gt 1) {
        $imageID = $response.imageID[0]
        }
    else {
        $imageID = $response.imageID
    }

    # Get all the versions from the first image
    $Objects = $response | Where-Object {$_.imageID -eq $imageID}
    $CurrentHubVersion = $Objects.tags
    WriteLog "$ServerURL=$CurrentHubVersion"

    Return $CurrentHubVersion

}

# RunProcess - start process
# - FilePath = string path to process executable
# - arguments = argument string to pass to process
# - ShouldWait = boolean: True = waits until process exits | False = returns to execution after starting process
# Returns process exit code if ShouldWait = true
Function RunProcess([String]$EXEPath,[String]$arguments,[Bool]$ShouldWait) {
      Write-Host "$($NewLine)Executing: $EXEPath $arguments"
      $ProcessInfo = New-Object System.Diagnostics.ProcessStartInfo
      $ProcessInfo.FileName = $EXEPath
      $ProcessInfo.Arguments = $arguments
      $Process = New-Object System.Diagnostics.Process
      $Process.StartInfo = $ProcessInfo
      $Process.Start() | Out-Null # Pipe out the "True" message, so that only process exit code is returned
      If ($ShouldWait) {
        Write-Host "Waiting for process to finish..."
        $Process.WaitForExit()
        Write-Host "Process finished with exit code $($Process.ExitCode)"
        Return $Process.ExitCode
      }
}

# CheckForError - prints message, result, and expected value.
# Continues script if result = expected value OR $ShouldTerminate = false.
# Stops script with error if result != expected value AND $ShouldTerminate = true.
Function CheckForError($ErrMessage, $ExpectedValue, $ResultValue, $ShouldTerminate) {
      If ($ResultValue -eq $ExpectedValue) {
        WriteLog "Success: $ErrMessage"
        Write-Host "Success: Expected ($ExpectedValue) = Result ($ResultValue) $NewLine"
      }
      Else {
        If ($ShouldTerminate) {
          Write-Host "Error: $ErrMessage"
          Write-Host "Error: Expected ($ExpectedValue) != Result ($ResultValue)"
          WriteLog "Published=Fail"
          Exit $ResultValue
        }
        Else {
          Write-Host "Warning: $ErrMessage"
          Write-Host "Warning: Expected ($ExpectedValue) != Result ($ResultValue)"
          Write-Host "Warning: Continuing script. $NewLine"
          $global:ScriptError = 0 # Reset script error level if this is a warning
        }
      }
}

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

# Pushes the image to Turbo.net Hub
Function TurboPublish($App,$Version,$ApiKey,$ServerURL) {
    $Repo = $App -replace '_','/'
    $Turbo = "C:\Program Files (x86)\Turbo\Cmd\turbo.exe"
    $ProcessExitCode = RunProcess $Turbo "config --domain=$ServerURL" $True
    CheckForError "Checking process exit code:" 0 $ProcessExitCode $True # Fail on turbo config failure
    $ProcessExitCode = RunProcess $Turbo "login --api-key $ApiKey" $True
    CheckForError "Checking process exit code:" 0 $ProcessExitCode $True # Fail on turbo login failure
    if ([string]::IsNullOrWhiteSpace($Version)) {
        $ProcessExitCode = RunProcess $Turbo "push $Repo" $True
        CheckForError "Checking process exit code:" 0 $ProcessExitCode $True # Fail on turbo push failure
        WriteLog "Published=$Repo"
    } else {
        $ProcessExitCode = RunProcess $Turbo "push $Repo $Repo`:$Version" $True
        CheckForError "Checking process exit code:" 0 $ProcessExitCode $True # Fail on turbo push failure
        WriteLog "Published=$Repo`:$Version"
    }
    

   
}

try {
    WriteLog "#################### $App #########################"
    WriteLog "Publishing $App version $AppVer to $ServerURL"
    TurboPublish -App $App -Version $AppVer -APIKey $APIKey -ServerURL $ServerURL

    # Read the result of the test log file for error
    $testLogFile = "$LocalLogsDir\!Publish.log"
    $fileContent = Get-Content $testLogFile
    $ErrorResultLine = $fileContent | Select-String "Published="
    $PublishResult = ($ErrorResultLine -split "=")[-1]
   
    if (($PublishResult -eq "Fail") -or (-not $fileContent)) {
        $ExitCode = 1 # Error or Fail
        $message = "Publish result: Fail!`n`nSee log files in:`n$LocalLogsDir`n"
    } else {
        $ExitCode = 0 # Success
        $message = "Test result: Success!`n`nPublished: $PublishResult`n`nSee log files in:`n$LocalLogsDir`n`n"
    }
}
finally {
    
    If ($ExitCode -eq 0) {
        Write-Output $message
        Show-Dialog -message $message -title "Successful!" -buttons "OK"
    } else {
        Write-Output $message
        Show-Dialog -message $message -title "Failed!" -buttons "OK"
    }
}