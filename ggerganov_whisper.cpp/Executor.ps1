param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$in = Join-Path -Path $PSScriptRoot -ChildPath "resources\gettysburg10.wav"
$out = Join-Path -Path ([Environment]::GetFolderPath("Desktop")) -ChildPath "out"
$ggml = "C:\ggml-tiny-q5_1.bin"

$image = "ggerganov/whisper.cpp"
$using = "ffmpeg/ffmpeg,microsoft/vcredist"
$isolate = "merge-user"
$extra = '--startup-file=powershell -- "C:\whisper.cpp\ConvertAndRun.ps1" -f ' + $in + ' -otxt -of ' + $out + ' -m ' + $ggml + $extra

# Download whisper GGML file.
if (-Not (Test-Path $ggml)) {
    Write-Host "Downloading whisper GGML..."
    $ProgressPreference = "SilentlyContinue"
    Invoke-WebRequest -Uri "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny-q5_1.bin" -OutFile $ggml -UseBasicParsing
    }

StandardTest -image $image -using $using -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir