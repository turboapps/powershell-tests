# PROBE (not for merge): VM-2932 validation. Runs the unchanged nodejs-lts test (test_body.py) and, pass or
# fail, records Microsoft Defender's detection events (1116/1117) into <Desktop>\nodejs_nodejs-lts-steps, which
# the harness uploads with the diagnostics. Before the fix Defender's Behavior:Win32/MZPEMemoryArtifacts.D
# killed container node.exe (node-gyp configure) with exit code 0.
script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
steps_dir = os.path.join(os.environ['USERPROFILE'], "Desktop", "nodejs_nodejs-lts-steps")

def defender_log(tag):
    if not os.path.exists(steps_dir):
        os.makedirs(steps_dir)
    out = os.path.join(steps_dir, "defender-%s.txt" % tag)
    ps = ("$e = @(Get-WinEvent -FilterHashtable @{LogName='Microsoft-Windows-Windows Defender/Operational'; Id=1116,1117} -ErrorAction SilentlyContinue); "
          "$e | Format-List TimeCreated,Id,Message | Out-File -Width 400 '%s'; "
          "'DEFENDER %s events=' + $e.Count + ' mzpe=' + @($e | Where-Object { $_.Message -match 'MZPEMemoryArtifacts' }).Count" % (out, tag))
    res = run('powershell -NoProfile -Command "%s"' % ps)
    for line in res.splitlines():
        if "DEFENDER" in line:
            Debug.user("PROBE %s" % line.strip())

defender_log("start")
try:
    execfile(os.path.join(script_path, "test_body.py"))
finally:
    defender_log("end")
