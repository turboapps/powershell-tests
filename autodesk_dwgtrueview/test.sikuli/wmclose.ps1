# PROBE ONLY - DO NOT MERGE.
#
# Replicates, from outside any container, exactly what the Turbo VM does to a
# sandboxed process when `turbo stop` asks it to exit gracefully -
# CSystemManager::TerminateSelfGracefullyCallback in vm/Vm/Engine/vm.cpp, whose
# window half is:
#
#     EnumWindows(_PostWmCloseIf, GetCurrentProcessId())
#       -> GetWindowThreadProcessId(hWnd, &pid)
#       -> if (pid == currentProcessId) PostMessageW(hWnd, WM_CLOSE, 0, 0)
#
# Every top-level window of the process, with no filter for visibility and none
# for whether the application is already on its way out.
#
# What this script deliberately leaves out is the rest of that callback: the
# CTRL_CLOSE_EVENT, the service stop, and the 10-second TerminateProcess timer.
# So if the crash reproduces under this and not only under `turbo stop`, the
# WM_CLOSE broadcast alone is sufficient and nothing about the VM or the
# container teardown is needed to explain it.
param([string]$ProcName = 'dwgviewr')

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class ProbeW {
    public delegate bool EnumProc(IntPtr h, IntPtr l);
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc cb, IntPtr l);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll", CharSet = CharSet.Unicode)] public static extern bool PostMessageW(IntPtr h, uint msg, IntPtr w, IntPtr l);
}
"@

$targets = @(Get-Process -Name $ProcName -ErrorAction SilentlyContinue | ForEach-Object { [int]$_.Id })
if ($targets.Count -eq 0) {
    Write-Output "wmclose: no $ProcName process, posted to 0 window(s)"
    exit 0
}

$posted = 0
$cb = [ProbeW+EnumProc] {
    param($h, $l)
    $owner = 0
    [void][ProbeW]::GetWindowThreadProcessId($h, [ref]$owner)
    if ($targets -contains [int]$owner) {
        # WM_CLOSE = 0x0010
        if ([ProbeW]::PostMessageW($h, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero)) {
            $script:posted++
        }
    }
    return $true
}
[void][ProbeW]::EnumWindows($cb, [IntPtr]::Zero)
Write-Output "wmclose: posted WM_CLOSE to $posted window(s) of $ProcName (pids: $($targets -join ','))"
