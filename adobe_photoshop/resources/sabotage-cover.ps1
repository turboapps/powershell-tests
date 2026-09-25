# SABOTAGE PROBE ONLY - not for merge.
# Emulates a slow Home page: after the relaunch, a topmost dark panel hides the
# Home area (everything below Photoshop's menu bar and header) for $Seconds, so
# the window is up but "Welcome to Photoshop" is not visible. $ShotDir gets a
# screenshot taken 60 s in, as evidence that the panel was up.
param([int]$Seconds = 150, [string]$ShotDir = "")
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$f = New-Object System.Windows.Forms.Form
$f.FormBorderStyle = 'None'
$f.StartPosition = 'Manual'
$f.ShowInTaskbar = $false
$f.TopMost = $true
$f.BackColor = [System.Drawing.Color]::FromArgb(38, 38, 38)
$f.Bounds = New-Object System.Drawing.Rectangle(0, 100, 1920, 900)
$close = New-Object System.Windows.Forms.Timer
$close.Interval = $Seconds * 1000
$close.Add_Tick({ $close.Stop(); $f.Close() })
$shot = New-Object System.Windows.Forms.Timer
$shot.Interval = 60000
$shot.Add_Tick({
    $shot.Stop()
    if ($ShotDir) {
        $bmp = New-Object System.Drawing.Bitmap(1920, 1080)
        $g = [System.Drawing.Graphics]::FromImage($bmp)
        $g.CopyFromScreen(0, 0, 0, 0, $bmp.Size)
        $g.Dispose()
        $bmp.Save((Join-Path $ShotDir 'zz-sabotage-cover-60s.jpg'), [System.Drawing.Imaging.ImageFormat]::Jpeg)
        $bmp.Dispose()
    }
})
$f.Add_Shown({ $close.Start(); $shot.Start() })
[System.Windows.Forms.Application]::Run($f)
