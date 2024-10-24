﻿param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$gguf = "C:\llama-2-7b-chat.Q4_K_M.gguf"
$image = "ggerganov/llama.cpp"
$using = "microsoft/vcredist"
$extra = '/C "C:\llama-avx2\llama-server.exe" -m ' + $gguf + ' -n 50 --port 8180 --chat-template llama2' + $extra

RunProcess -path "cmd.exe"

# Download llama GGUF file.
if (-Not (Test-Path $gguf)) {
    Write-Host "Downloading llama GGUF..."
    $ProgressPreference = "SilentlyContinue"
    Invoke-WebRequest -Uri "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf" -OutFile $gguf -UseBasicParsing
    }

StandardTest -image $image -using $using -extra $extra -shouldInstall $False -localLogsDir $localLogsDir