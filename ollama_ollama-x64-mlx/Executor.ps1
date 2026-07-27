param (
        [string]$extra,
        [string]$localLogsDir
    )

$IncludePath = Join-Path -Path $PSScriptRoot -ChildPath "..\!include\Test.ps1"
. $IncludePath

## Ollama MLX is an addon image for ollama/ollama-x64, so it is tested by layering it over
## the base image with --using (same pattern as irfanview/irfanview-plugins).
## Ollama is a headless server application, so this test does not use SikuliX.
## The test starts the base image (default startup file runs "ollama serve") with the addon
## and the gemma4:e4b model image merged in, waits for the HTTP API on localhost:11434,
## verifies the model is available and runs a chat completion.
## Results are written to <image>-test.log which TestPS.ps1 scans for "error" lines.

$image = "ollama/ollama-x64-mlx"
$app = "ollama/ollama-x64"
$using = "ollama/ollama-x64-mlx,ollama/ollama-model-gemma4:e4b"  # Addon under test + test model image
$TestModel = "gemma4:e4b"
$OllamaUrl = "http://localhost:11434"

if ([string]::IsNullOrWhiteSpace($localLogsDir)) {
    $localLogsDir = "$env:USERPROFILE\Desktop"
}
$name = $image -replace '[/]', '_'
$testLog = Join-Path $localLogsDir "$name-test.log"
$logLines = @()

PrepareTest -image $image -localLogsDir $localLogsDir
PullTurboImages -image $app -using $using

# Start the server detached with the MLX addon and model image layered over the base image.
TryTurboApp -image $app -using $using -extra $extra -detached $True

try {
    # Wait for the API to come up.
    $ready = $False
    for ($i = 0; $i -lt 60; $i++) {
        try {
            $version = Invoke-RestMethod -Uri "$OllamaUrl/api/version" -TimeoutSec 5
            $ready = $True
            break
        } catch {
            Start-Sleep -Seconds 5
        }
    }
    if (-not $ready) {
        throw "Ollama server did not respond on $OllamaUrl within the timeout."
    }
    $logLines += "PASS: Server is up with MLX addon. Version = $($version.version)"

    # Verify the layered model image is visible to the server.
    $tags = Invoke-RestMethod -Uri "$OllamaUrl/api/tags" -TimeoutSec 30
    if (-not ($tags.models | Where-Object { $_.name -eq $TestModel })) {
        throw "Model $TestModel from the layered image is not listed by the server. Models found: $($tags.models.name -join ', ')"
    }
    $logLines += "PASS: Model $TestModel is available from the layered image."

    # Run a chat completion and verify a non-empty response.
    $chatBody = @{
        model = $TestModel
        messages = @(@{ role = "user"; content = "Reply with the word hello." })
        stream = $False
    } | ConvertTo-Json -Depth 5
    $chatResult = Invoke-RestMethod -Uri "$OllamaUrl/api/chat" -Method Post -Body $chatBody -ContentType "application/json" -TimeoutSec 600
    if ([string]::IsNullOrWhiteSpace($chatResult.message.content)) {
        throw "Chat completion returned an empty response."
    }
    $logLines += "PASS: Chat completion returned a response: $($chatResult.message.content)"
    $logLines += "Test finished successfully."
    $TestResult = 0
} catch {
    $logLines += "ERROR: $($_.Exception.Message)"
    $TestResult = 1
} finally {
    # Stop the detached session started by TryTurboApp.
    turbo stop test
    Set-Content -Path $testLog -Value $logLines
}

exit $TestResult
