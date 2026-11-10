# PROBE (not for merge): VM-2929 A/B on the CI runner, hosted in the 7-zip-x64 job.
# Runs the VM team's BVT guest TestStdStreamsDump.exe inside a `turbo run clean`
# container on whatever xvm the run overrides (util.read_extra() carries --vm=).
# xvm 26.11.2 should crash a round with 0xC0000409 (std::length_error out of the
# WriteFile hook); 26.11.16.1344 (fix 2b4f384a9) should finish every round.
script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
import shutil
addImagePath(include_path)
setAutoWaitTimeout(20)
util.pre_test()

wait("zip_add.png", 60)
type(Key.F4, Key.ALT)
wait(5)

# Into the step-frames folder, which the harness uploads with the diagnostics.
work = os.path.join(util.desktop, "7-zip_7-zip-x64-steps", "vm2929")
if os.path.exists(work):
    shutil.rmtree(work)
shutil.copytree(os.path.join(script_path, os.pardir, "vm2929"), work)

extra = util.read_extra()
Debug.user("PROBE extra:%s" % extra)
cmd = ('turbo run 7-zip/7-zip-x64 --offline --isolate=merge-user --name=vm2929 --startup-file=cmd.exe%s -- /c "%s"' %
       (extra, os.path.join(work, "vm2929.cmd")))
Debug.user("PROBE cmd: %s" % cmd)
out = run(cmd)
for line in out.splitlines():
    Debug.user("PROBE turbo: %s" % line)
run("turbo stop vm2929")
run('cmd /c "turbo vms > "%s""' % os.path.join(work, "turbo-vms.txt"))

for name in ["vm2929-result.txt", "vm2929-normal.txt", "vm2929-exitrounds.txt"]:
    path = os.path.join(work, name)
    text = open(path).read() if os.path.exists(path) else "(missing)"
    for line in text.splitlines():
        Debug.user("PROBE %s: %s" % (name, line))

result_path = os.path.join(work, "vm2929-result.txt")
result = open(result_path).read() if os.path.exists(result_path) else ""
if "DONE" not in result:
    raise FindFailed("PROBE INVALID: repro script did not finish (no DONE in vm2929-result.txt)")
if "NORMAL_EXIT=0" not in result or "EXITROUNDS_EXIT=0" not in result:
    raise FindFailed("PROBE VM-2929 REPRO: a TestStdStreamsDump round failed: %s" % " | ".join(result.split()))
Debug.user("PROBE VM-2929 NOT reproduced: all rounds exited 0")
