param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Create firewall rules to prvent prompt
New-NetFirewallRule -DisplayName "Allow node" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow -Profile Any
New-NetFirewallRule -DisplayName "Allow node" -Direction Inbound -Protocol UDP -LocalPort 3000 -Action Allow -Profile Any

$image = "nodejs/nodejs-lts"
# Launch the locally imported 22.23.4 capture; -image still selects this test and its log names
$app = "nodejs/nodejs-lts:22.23.4"
$using = "python/python-x64,microsoft/vsbuildtools"
$extra = $extra + " --enable=usedllinjection --working-dir=" + $PSScriptRoot + "\resources "

StandardTest -image $image -app $app -using $using -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir