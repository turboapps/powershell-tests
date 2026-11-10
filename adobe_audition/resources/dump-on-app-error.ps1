# Probe helper (not for merge): if a legacy "Application Error" box is on screen, write a full memory
# dump of every CEPHtmlEngine.exe (the crashing process sits inside that box, so WER never writes one)
# into the test's step-frames folder, which the CI harness uploads in <app>-diagnostics.
# Prints APP_ERROR_FOUND when a box was found.
param([string]$OutDir, [string]$ProcessName = 'CEPHtmlEngine')
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force $OutDir | Out-Null
Add-Type @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
public static class ProbeWin {
    delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc f, IntPtr l);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    public static List<string> Titles() {
        var r = new List<string>();
        EnumWindows((h, l) => {
            if (!IsWindowVisible(h)) return true;
            var sb = new StringBuilder(512); GetWindowText(h, sb, 512);
            uint pid; GetWindowThreadProcessId(h, out pid);
            if (sb.Length > 0) r.Add(pid + "\t" + sb.ToString());
            return true; }, IntPtr.Zero);
        return r;
    }
    [DllImport("dbghelp.dll", SetLastError = true)]
    public static extern bool MiniDumpWriteDump(IntPtr hProcess, uint pid, Microsoft.Win32.SafeHandles.SafeFileHandle hFile,
        uint type, IntPtr exc, IntPtr user, IntPtr cb);
}
'@
$titles = [ProbeWin]::Titles()
$hits = @($titles | Where-Object { $_ -match 'Application Error|has stopped working|CEPHtmlEngine' })
$stamp = Get-Date -Format 'HHmmss'
$titles | Set-Content (Join-Path $OutDir "windows-$stamp.txt")
if ($hits.Count -eq 0) { Write-Output 'NO_APP_ERROR'; exit 0 }
Write-Output 'APP_ERROR_FOUND'
$hits | ForEach-Object { Write-Output "  window: $_" }
# MiniDumpWithFullMemory | MiniDumpWithHandleData | MiniDumpWithThreadInfo | MiniDumpWithUnloadedModules
$type = 0x2 -bor 0x4 -bor 0x1000 -bor 0x20
foreach ($p in Get-Process -Name $ProcessName -ErrorAction SilentlyContinue) {
    $file = Join-Path $OutDir ("{0}.{1}.probe.dmp" -f $ProcessName, $p.Id)
    $fs = [System.IO.File]::Create($file)
    $ok = [ProbeWin]::MiniDumpWriteDump($p.Handle, [uint32]$p.Id, $fs.SafeFileHandle, [uint32]$type, [IntPtr]::Zero, [IntPtr]::Zero, [IntPtr]::Zero)
    $err = [Runtime.InteropServices.Marshal]::GetLastWin32Error()
    $fs.Close()
    Write-Output ("  dump {0} pid {1}: ok={2} err={3} size={4}" -f $file, $p.Id, $ok, $err, (Get-Item $file).Length)
}
