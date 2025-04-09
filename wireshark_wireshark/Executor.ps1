param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$image = "wireshark/wireshark"
$using = "turbobuild/isolate-edge-wc"


# Need to install Npcap first.
$installerUrl = "https://npcap.com/dist/npcap-1.79.exe"
$installerPath = "$env:USERPROFILE\Desktop\installer.exe"
Invoke-WebRequest -Uri $installerUrl -OutFile $installerPath
# RunProcess -path $installerPath
$command = "turbo run sikulixide --name=npcap-install --using=oracle/jre-x64 --offline --disable=spawnvm --isolate=merge-user --startup-file=java -- -jar @SYSDRIVE@\SikulixIDE\sikulixide-2.0.5.jar -r $($PSScriptRoot)\npcap.sikuli -f $($localLogsDir)\npcap-install.log"
Invoke-Expression $command

StandardTest -image $image -using $using -extra $extra -localLogsDir $localLogsDir