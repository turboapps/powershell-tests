param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

$in = Join-Path -Path $PSScriptRoot -ChildPath "resources\gettysburg10.wav"
$out = Join-Path -Path ([Environment]::GetFolderPath("Desktop")) -ChildPath "out"
$ggml = "C:\ggml-tiny-q5_1.bin"

$image = "ggerganov/whisper-cpp"
$using = "ffmpeg/ffmpeg,microsoft/vcredist"
$isolate = "merge-user"
# Leading space is required: on client/XVM override runs $extra arrives non-empty
# (e.g. "--vm=26.3.18.1034"); without the space the tokens fuse into
# "--vm=26.3.18.1034--startup-file=powershell" and turbo rejects it ("Only
# alphanumeric characters ... allowed in release names"), so the app never
# launches and the test fails its output-file assert.
$extra = $extra + ' --startup-file=powershell -- "C:\whisper.cpp\ConvertAndRun.ps1" -f ' + $in + ' -otxt -of ' + $out + ' -m ' + $ggml + ' '

# Download whisper GGML file.
if (-Not (Test-Path $ggml)) {
    Write-Host "Downloading whisper GGML..."
    $ProgressPreference = "SilentlyContinue"
    Invoke-WebRequest -Uri "https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny-q5_1.bin" -OutFile $ggml -UseBasicParsing
    }

StandardTest -image $image -using $using -isolate $isolate -extra $extra -shouldInstall $False -localLogsDir $localLogsDir