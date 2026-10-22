param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

# Create firewall rules to prevent the prompt
New-NetFirewallRule -DisplayName "Allow php" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Any
New-NetFirewallRule -DisplayName "Allow php" -Direction Inbound -Protocol UDP -LocalPort 8000 -Action Allow -Profile Any

# php.exe is the image's default startup file. Start its built-in web server on port 8000 with
# resources\www (index.php) as the document root; test.py browses to http://localhost:8000.
$image = "php/php"
$ciExtra = $extra
$extra = $extra + ' -- -S 127.0.0.1:8000 -t "' + $PSScriptRoot + '\resources\www" '

StandardTest -image $image -extra $extra -testExtra $ciExtra -shouldInstall $False -localLogsDir $localLogsDir
