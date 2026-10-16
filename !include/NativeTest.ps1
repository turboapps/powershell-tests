# Helpers for native-app tests: tests with no build behind them (microsoft_edge-x64-native
# and its siblings). The app is installed natively on the test VM from the vendor's
# latest installer, downloaded the way the corresponding powershell-builds
# BuildTurboImage.ps1 downloads it, and then launched in a base container with
# --startup-file pointing at the native executable. Nothing app-specific is pulled from
# a hub, so the test's .applab.yml sets publish: false.
#
# Dot-source after Test.ps1 (uses its RunProcess).

# The app-tests VM image locks Edge to the version baked into it (applab
# images/shared/UpdateEdge.ps1) by blocking MicrosoftEdgeUpdate.exe's outbound traffic.
# The Edge and WebView2 installers run MicrosoftEdgeUpdate.exe and fail behind that rule.
function Remove-EdgeUpdateBlock {
    $rules = Get-NetFirewallRule -DisplayName "Block EdgeUpdate Outbound" -ErrorAction SilentlyContinue
    if ($rules) {
        $rules | Remove-NetFirewallRule
        Write-Host "Removed firewall rule: Block EdgeUpdate Outbound"
    } else {
        Write-Host "Firewall rule not present: Block EdgeUpdate Outbound"
    }
}

# Download an installer to the desktop Installers folder, as powershell-builds'
# DownloadInstaller does (wget, ie Invoke-WebRequest), and return its path.
function Save-NativeInstaller {
    param (
        [string]$DownloadLink,
        [string]$InstallerName
    )

    $downloadPath = "$env:USERPROFILE\Desktop\Installers"
    New-Item -ItemType Directory -Path $downloadPath -Force | Out-Null
    $installer = Join-Path $downloadPath $InstallerName

    Write-Host "Downloading $DownloadLink to $installer"
    # The progress bar slows Invoke-WebRequest by an order of magnitude on Windows PowerShell 5.1.
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $DownloadLink -OutFile $installer -UseBasicParsing
    $hash = (Get-FileHash $installer -Algorithm SHA256).Hash
    Write-Host "DownloadHash=sha256:$($hash.ToLower())"

    return $installer
}

# Run an installer and throw unless it succeeded (0, or 3010 = success, reboot required).
function Invoke-NativeInstaller {
    param (
        [string]$Path,
        [string]$Arguments
    )

    $exitCode = RunProcess -path $Path -arguments $Arguments -shouldWait $True
    if ($exitCode -ne 0 -and $exitCode -ne 3010) {
        throw "$Path $Arguments exited $exitCode"
    }
}

# The latest Edge enterprise release for a channel ("Stable" or "Beta"), selected from the
# Edge product API as powershell-builds microsoft_edge-x64(-beta)/BuildTurboImage.ps1 does.
function Get-EdgeEnterpriseRelease {
    param (
        [string]$Channel,
        [string]$Architecture = "x64",
        [string]$Platform = "Windows"
    )

    $edgeEnterpriseMSIUri = 'https://edgeupdates.microsoft.com/api/products?view=enterprise'
    $response = Invoke-WebRequest -Uri $edgeEnterpriseMSIUri -Method Get -ContentType "application/json" -UseBasicParsing
    $jsonObj = ConvertFrom-Json $([String]::new($response.Content))

    $selectedIndex = [array]::indexof($jsonObj.Product, "$Channel")

    $selectedVersion = (([Version[]](($jsonObj[$selectedIndex].Releases |
        Where-Object { $_.Architecture -eq $Architecture -and $_.Platform -eq $Platform }).ProductVersion) |
        Sort-Object -Descending)[0]).ToString(4)

    return $jsonObj[$selectedIndex].Releases |
        Where-Object { $_.Architecture -eq $Architecture -and $_.Platform -eq $Platform -and $_.ProductVersion -eq $selectedVersion }
}

# The installed msedge.exe of a channel, or $null. Edge installs under Program Files (x86)
# on x64; on Windows on ARM it can be either, so both are checked (as applab's
# images/shared/UpdateEdge.ps1 does).
function Get-NativeEdgeExe {
    param (
        [string]$Channel
    )

    $folder = if ($Channel -eq "Beta") { "Edge Beta" } else { "Edge" }
    foreach ($root in @("C:\Program Files (x86)", "C:\Program Files")) {
        $exe = "$root\Microsoft\$folder\Application\msedge.exe"
        if (Test-Path $exe) { return $exe }
    }
    return $null
}

# Install the latest Edge enterprise MSI of a channel and architecture natively and
# return the installed msedge.exe path. The VM image already carries Stable Edge: when
# it is already at (or, from Windows Update, ahead of) the channel's latest, the MSI is
# skipped, because msiexec fails a downgrade with 1603.
function Install-NativeEdge {
    param (
        [ValidateSet("Stable", "Beta")]
        [string]$Channel,
        [ValidateSet("x64", "arm64")]
        [string]$Architecture = "x64"
    )

    $release = Get-EdgeEnterpriseRelease -Channel $Channel -Architecture $Architecture
    $latest = $release.ProductVersion
    Write-Host "Latest Edge $Channel $Architecture enterprise release: $latest"

    $exe = Get-NativeEdgeExe -Channel $Channel
    $installed = if ($exe) { (Get-Item $exe).VersionInfo.ProductVersion } else { $null }
    if ($installed -and [version]$installed -ge [version]$latest) {
        Write-Host "Installed Edge $Channel $installed is current - not reinstalling"
    } else {
        if ($installed) { Write-Host "Installed Edge $Channel $installed is older - upgrading" }

        $msi = @($release.Artifacts | Where-Object { $_.ArtifactName -eq "msi" })[0]
        # The artifact's own file name, eg MicrosoftEdgeBetaEnterpriseARM64.msi.
        $installerName = Split-Path ([uri]$msi.Location).AbsolutePath -Leaf
        $installer = Save-NativeInstaller -DownloadLink $msi.Location -InstallerName $installerName
        Invoke-NativeInstaller -Path "msiexec.exe" -Arguments "/I `"$installer`" /qn /L*V `"$env:USERPROFILE\Desktop\Installers\$installerName.log`""

        $exe = Get-NativeEdgeExe -Channel $Channel
        $installed = if ($exe) { (Get-Item $exe).VersionInfo.ProductVersion } else { $null }
        if ($installed -ne $latest) {
            throw "Edge $Channel is '$installed' after the install, expected $latest"
        }
    }
    Write-Host "Edge $Channel $installed at $exe"

    return $exe
}

# Edge policies the powershell-builds Edge images carry, set natively so the native
# browser behaves like the captured one under the same sikulix test.
function Set-NativeEdgePolicies {
    # No first run prompts, and no second launch "What are you interested in" prompt.
    &reg.exe ADD "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v HideFirstRunExperience /t REG_DWORD /d 1 /f
    &reg.exe ADD "HKLM\Software\Policies\Microsoft\MicrosoftEdge\Main" /v PreventFirstRunPage /t REG_DWORD /d 1 /f
    &reg.exe ADD "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v NewTabPageContentEnabled /t REG_DWORD /d 0 /f
    # Background msedge.exe processes would keep the container running after Edge is closed.
    &reg.exe ADD "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v BackgroundModeEnabled /t REG_DWORD /d 0 /f
    &reg.exe ADD "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v StartupBoostEnabled /t REG_DWORD /d 0 /f
    &reg.exe ADD "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v AudioSandboxEnabled /t REG_DWORD /d 0 /f
}

# Run Edge's first run user setup and seed the profile's "Local State" (a profile that has
# launched Edge twice), which the powershell-builds images do to prevent the second launch
# "What's new" tab. $UserDataDir is the --user-data-dir the test launches Edge with.
function Initialize-NativeEdgeProfile {
    param (
        [string]$Exe,
        [string]$SetupSwitches,
        [string]$UserDataDir,
        [string]$LocalState
    )

    $version = (Get-Item $Exe).VersionInfo.ProductVersion
    $setup = Join-Path (Split-Path $Exe -Parent) "$version\Installer\setup.exe"
    RunProcess -path $setup -arguments "--configure-user-settings --verbose-logging --system-level $SetupSwitches" -shouldWait $True | Out-Null

    New-Item -ItemType Directory -Path $UserDataDir -Force | Out-Null
    Copy-Item -Path $LocalState -Destination $UserDataDir -Force
}

# Install the WebView2 Evergreen runtime natively from the bootstrapper powershell-builds
# microsoft_edgewebview2 uses. The bootstrapper always installs (or updates to) the latest.
function Install-NativeWebView2 {
    $clientKey = "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
    $before = (Get-ItemProperty $clientKey -ErrorAction SilentlyContinue).pv
    Write-Host "WebView2 runtime before install: '$before'"

    $installer = Save-NativeInstaller -DownloadLink "https://go.microsoft.com/fwlink/p/?LinkId=2124703" -InstallerName "MicrosoftEdgeWebview2Setup.exe"
    Invoke-NativeInstaller -Path $installer -Arguments "/silent /install"

    $after = (Get-ItemProperty $clientKey -ErrorAction SilentlyContinue).pv
    if (-not $after) { throw "WebView2 runtime not registered after the install" }
    Write-Host "WebView2 runtime after install: $after"
}

# Make WebView2 apps load the Beta channel runtime (installed with Edge Beta) instead of
# the Stable runtime, with the policies powershell-builds microsoft_edgewebview2-beta sets.
# ChannelSearchKind 1 = search least stable channel first. ReleaseChannels "1" = only Beta.
function Set-NativeWebView2BetaPolicies {
    &reg.exe ADD "HKLM\SOFTWARE\Policies\Microsoft\Edge\WebView2\ChannelSearchKind" /v "*" /t REG_DWORD /d 1 /f
    &reg.exe ADD "HKLM\SOFTWARE\Policies\Microsoft\Edge\WebView2\ReleaseChannels" /v "*" /t REG_SZ /d "1" /f
    &reg.exe ADD "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v BackgroundModeEnabled /t REG_DWORD /d 0 /f
    &reg.exe ADD "HKLM\SOFTWARE\Policies\Microsoft\Edge" /v StartupBoostEnabled /t REG_DWORD /d 0 /f
}

# Install Power BI Desktop natively, as the WebView2 host app the microsoft_edgewebview2
# tests drive. Same installer and switches as powershell-builds powerbi_powerbi; returns
# the installed PBIDesktop.exe path.
function Install-NativePowerBI {
    $installer = Save-NativeInstaller -DownloadLink "https://download.microsoft.com/download/8/8/0/880BCA75-79DD-466A-927D-1ABF1F5454B0/PBIDesktopSetup_x64.exe" -InstallerName "PBIDesktopSetup_x64.exe"
    Invoke-NativeInstaller -Path $installer -Arguments "-q ACCEPT_EULA=1 DISABLE_UPDATE_NOTIFICATION=1 ENABLECXP=0"

    $exe = "C:\Program Files\Microsoft Power BI Desktop\bin\PBIDesktop.exe"
    if (-not (Test-Path $exe)) { throw "$exe not found after the install" }
    Write-Host "Power BI Desktop $((Get-Item $exe).VersionInfo.ProductVersion) at $exe"

    return $exe
}

# Run the native setup steps; on failure, write the reason to the test log the CI harness
# reads (so the run fails with it rather than as "no-log") and end the executor.
function Invoke-NativeSetup {
    param (
        [string]$image,
        [string]$localLogsDir,
        [scriptblock]$Setup
    )
    if ([string]::IsNullOrWhiteSpace($localLogsDir)) {
        $localLogsDir = "$env:USERPROFILE\Desktop"
    }

    try {
        & $Setup
    } catch {
        $name = $image -replace '[/]', '_'
        Write-Host "Native setup failed: $_"
        "[error] native setup failed: $_" | Set-Content "$localLogsDir\$name-test.log"
        Write-TestDoneMarker -image $image -exitCode 1 -logFile "$localLogsDir\$name-test.log"
        exit 1
    }
}

# Launch a native executable in a base container named "test" (detached), and record the
# launch in <test>\launch.txt for the sikulix test's own relaunches (see test.py's
# launch()): line 1 is the turbo command line up to the app arguments, line 2 the app
# arguments. $extra (the CI harness's flags, eg --vm=) goes before the "--".
function Start-NativeApp {
    param (
        [string]$image,
        [string]$exe,
        [string]$appArgs,
        [string]$extra
    )

    $name = $image -replace '[/]', '_'
    $command = "run base --name=test --isolate=merge-user --startup-file=`"$exe`" --enable=usedllinjection,cachefileinfo --network=test --disable-proxy-resolve-via-proxy"
    if (-not [string]::IsNullOrWhiteSpace($extra)) {
        $command += " $extra"
    }
    Set-Content -Path "$PSScriptRoot\..\$name\launch.txt" -Value @("turbo $command", $appArgs)

    $arguments = "$command -d"
    if (-not [string]::IsNullOrWhiteSpace($appArgs)) {
        $arguments += " -- $appArgs"
    }
    RunProcess -path "turbo.exe" -arguments $arguments -shouldWait $False
}
