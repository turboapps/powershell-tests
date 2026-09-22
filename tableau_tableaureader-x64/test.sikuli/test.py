# PROBE ONLY - DO NOT MERGE.
#
# A/B for the tableau sc.exe crash-dump failures (VM-2896). App Tests run
# 35678863980 failed tableau_tableaureader-x64 with the SikuliX script passing
# end to end and the job failed by the crash-dump gate alone: sc.exe died with
# c0000005, EXECUTE fault at 0x13346, which is not in any loaded module.
#
# sc.exe's import table is completely unbound - every IAT slot still holds the
# on-disk RVA of its own IMAGE_IMPORT_BY_NAME record - so the first call through
# a thunk leaves the address space:
#
#     sc.exe+0xD4A0 (IAT) = 0x13346 -> sc.exe+0x13346 = 0c 00 "__C_specific_handler"
#     sc.exe+0xD4F0 (IAT) = 0x130b6 -> sc.exe+0x130b6 = 37 00 "_initterm_e"
#
# The crashing process is spawned inside the container:
#
#     C:\Windows\System32\sc  stop "FlexNet Licensing Service 64"
#     working dir: C:\Program Files\Tableau\Tableau Reader 2026.2\bin\
#
# and in every recorded occurrence it was created while `turbo stop test` was
# tearing the container down - the dump lands 1-4 s after the stop command and
# before the session finishes exiting:
#
#     run 35678863980 (reader, 26.9.48): stop 21:15:54.9 -> sc.exe start ~21:15:55
#                                        -> dump 21:15:58 -> session gone 21:16:01
#     runs 35002798650 / 35002810972 / 35022008056 (public, 26.9.47): 2-4 s after
#
# That timing is the whole of the evidence for the teardown race, and it is what
# VM-2896's repro note lists as its first open question ("insert a 15-30 s wait
# between the close and the stop - if the dumps stop, sc.exe is being created
# while the VM is already unloading"). This probe answers it.
#
# Two arms, alternating inside one job so the same pool VM and the same load
# carry both:
#
#   stop-races  Exit, then `turbo stop test` straight away. Production.
#   stop-after  Exit, wait for tabreader.exe to leave the process list, THEN
#               `turbo stop test`.
#
# Cycle 1 is given to stop-after: it is the only launch with a cold profile, so
# if a dump needs a first launch rather than the stop overlap, the free hit goes
# to the arm the hypothesis says should be clean.
#
# Nothing is assumed about which process writes the dump: every new *.dmp in the
# crash dump directory is attributed to the cycle that produced it, and the
# sc.exe ones are tallied separately, since sc.exe is the victim VM-2896
# describes and tabreader.exe dying would be a different finding.

script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

import subprocess

setAutoWaitTimeout(60)
util.pre_test()

# The launch the executor made before this script started (Test.ps1 TryTurboApp),
# repeated verbatim for every cycle after the first so each cycle closes the same
# kind of instance the production failure closed: a `turbo try` session named
# "test", not the Start Menu shortcut.
LAUNCH = ("turbo " + util.try_verb() + " tableau/tableaureader-x64 --name=test"
          " --enable=disablefontpreload,usedllinjection,cachefileinfo"
          " --network=test --disable-proxy-resolve-via-proxy"
          " --using=turbobuild/isolate-edge-wc -d"
          + util.read_extra())

# Where the workflow's "Enable crash dumps" step points WER LocalDumps for this
# job. The environment variable is what the workflow sets; the literal is the
# value it has had in every run and is the fallback for when the variable does
# not survive into the sikulixide container.
CRASH_DIR = os.environ.get("CRASH_DUMP_DIR") or "C:\\actions-runner\\_work\\_temp\\crashdumps"

CYCLES = 8
ARMS = ["stop-after", "stop-races"]

# --------------------------------------------------------------------------
# Probe helpers
# --------------------------------------------------------------------------

def dump_names():
    try:
        return sorted([f for f in os.listdir(CRASH_DIR) if f.lower().endswith(".dmp")])
    except (OSError, IOError):
        return []

def live_pids(image="tabreader.exe"):
    pids = []
    for line in run('tasklist /FI "IMAGENAME eq %s" /NH /FO CSV' % image).splitlines():
        fields = [f.strip().strip('"') for f in line.split('","')]
        if len(fields) >= 2 and fields[0].lower() == image.lower():
            pids.append(fields[1])
    return pids

def process_gone(image="tabreader.exe"):
    return not live_pids(image)

# Wait for the application's own exit to finish. Returns the seconds it took, or
# -1 if it never went away. A crash also takes the process off the list, so this
# returns on a crashed exit too - which is the point: the stop-after arm has to
# be able to record a crash of its own.
def wait_process_gone(image="tabreader.exe", max_wait=120, poll=2):
    waited = 0
    while waited < max_wait:
        if process_gone(image):
            return waited
        wait(poll)
        waited += poll
    return -1

# WerSvc spawns WerFault a moment after the fault and WerFault writes the dump
# after the crashed process is already gone, so a dump can still be in flight
# when the cycle ends. Same shape as the gate's own wait in Invoke-AppTest.ps1:
# a short grace so WerFault has started, then bounded waiting for it to finish.
def settle_dumps(grace=8, max_wait=90, poll=3):
    wait(grace)
    waited = 0
    while waited < max_wait:
        if "WerFault" not in run('tasklist /FI "IMAGENAME eq WerFault.exe" /NH'):
            break
        wait(poll)
        waited += poll
    return dump_names()

# Take the recorded dumps out of the folder before the next cycle. WER's
# DumpCount is 5: past that it REPLACES the oldest dump rather than declining to
# write, so over eight cycles the folder would stop being a record of what
# crashed. The per-cycle tally does not depend on the delete reaching the host -
# `new` is a diff against the listing this script last saw, and the listing is
# re-read after the purge either way.
def purge_dumps(names):
    removed = 0
    for name in names:
        try:
            os.remove(os.path.join(CRASH_DIR, name))
            removed += 1
        except (OSError, IOError):
            pass
    if names:
        Debug.user("probe: purge removed %d of %d dump(s), %d still listed"
                   % (removed, len(names), len(dump_names())))

# Put the machine back where cycle 1 found it, whatever the cycle left behind: a
# dialog nothing dismissed, an instance that never finished loading, a container
# still up. taskkill terminates rather than faulting, so nothing here can write a
# dump of its own and inflate the next cycle's count.
# Never name conhost.exe here. The harness's own PowerShell is hosted by one, and
# killing every conhost on the box takes the job's console with it: probe runs
# 35776009034 / 35776018836 / 35776027615 / 35776036449 / 35776046182 all died
# with 0xC0000142 and staged no artifacts at all, so eight measured cycles per
# job were lost. Kill only the app's own processes.
def reset_between_cycles():
    type(Key.ESC)
    wait(1)
    run("turbo stop test")
    for image in ("tabreader.exe", "tabprotosrv.exe"):
        os.system('cmd /c taskkill /f /im "%s" /t' % image)
    wait(5)

def launch():
    # Leave no session behind for the new one to collide with. Unconditional: a
    # stop with nothing to stop is a no-op. Outside the measured window on
    # purpose - by here the previous cycle's close is long finished, so this stop
    # can never be the one that races a teardown.
    run("turbo stop test")
    wait(5)
    subprocess.Popen(LAUNCH)
    wait(10)

# The registration dialog is what a fresh Tableau Reader launch comes up with,
# and it is what the production test drives. Returns True once it is on screen.
#
# It returns rather than raises because a probe that dies on the first launch it
# cannot read throws away every cycle after it.
def wait_app_loaded(timeout=120):
    if exists("tableau_reg.png", timeout):
        click(Pattern("tableau_reg.png").targetOffset(-289, 0))
        return True
    Debug.user("probe: tableau_reg.png never appeared in %d s" % timeout)
    return False

# The production test's close: Alt+F4 raises Tableau's "the license on your
# system has changed" prompt, the first click clears its "Restart the
# application" box and the second presses Exit. That Exit is what starts the
# shutdown which spawns `sc stop "FlexNet Licensing Service 64"`.
#
# Returns True if the prompt was driven, False if it never appeared - in which
# case Alt+F4 alone has closed the window and the cycle still measures a close,
# so it is logged rather than skipped.
def close_app():
    type(Key.F4, Key.ALT)
    if not exists("tableau_reg_exit.png", 30):
        Debug.user("probe: the license prompt did not appear after Alt+F4")
        return False
    click(Pattern("tableau_reg_exit.png").targetOffset(-139, 10))
    click(Pattern("tableau_reg_exit.png").targetOffset(99, 52))
    return True

# --------------------------------------------------------------------------
# The two arms. They differ in one line.
# --------------------------------------------------------------------------

def close_stop_races():
    close_app()
    run("turbo stop test")
    return None

def close_stop_after():
    close_app()
    gone = wait_process_gone()
    run("turbo stop test")
    return gone

# --------------------------------------------------------------------------
# Run the cycles
# --------------------------------------------------------------------------

Debug.user("probe: crash dump dir %s (readable: %s, %d dump(s) already there)"
           % (CRASH_DIR, os.path.isdir(CRASH_DIR), len(dump_names())))
Debug.user("probe: launch command for cycles 2..%d: %s" % (CYCLES, LAUNCH))

records = []
seen_dumps = dump_names()

for cycle in range(1, CYCLES + 1):
    arm = ARMS[(cycle - 1) % len(ARMS)]

    # Cycle 1 uses the instance the executor already launched; every later cycle
    # launches its own so it closes the same kind of session. Retry once through
    # a full reset: a launch that follows a crashed cycle can come up with
    # nothing on screen at all.
    loaded = False
    for attempt in range(2):
        if cycle > 1 or attempt > 0:
            launch()
        if wait_app_loaded():
            loaded = True
            break
        Debug.user("probe: cycle %d launch attempt %d came up empty" % (cycle, attempt + 1))
        reset_between_cycles()

    if not loaded:
        # Not an observation either way: the close this probe measures never
        # happened. Still drain the dump folder, so a dump from a launch that
        # died on its way up is reported here and not charged to the next cycle.
        stray = settle_dumps()
        stray_new = [d for d in stray if d not in seen_dumps]
        purge_dumps(stray)
        seen_dumps = dump_names()
        records.append((cycle, "skipped", [], None, stray_new))
        Debug.user("probe: cycle %d SKIPPED (would have been %s) stray_dumps=%s"
                   % (cycle, arm, ",".join(stray_new) or "none"))
        reset_between_cycles()
        continue

    pids = live_pids()

    if arm == "stop-races":
        gone = close_stop_races()
    else:
        gone = close_stop_after()

    now = settle_dumps()
    new = [d for d in now if d not in seen_dumps]
    purge_dumps(now)
    seen_dumps = dump_names()

    records.append((cycle, arm, pids, gone, new))
    Debug.user("probe: cycle %d arm=%s pids=%s exit_after=%s new_dumps=%s"
               % (cycle, arm, ",".join(pids) or "none",
                  "n/a" if gone is None else ("never" if gone < 0 else "%ds" % gone),
                  ",".join(new) or "none"))

    # The stop-races arm leaves the container being torn down; give the session
    # the same moment to disappear the production test's `turbo stop` gets before
    # the next launch. Outside the measured window.
    wait(10)
    reset_between_cycles()

# --------------------------------------------------------------------------
# Tally. Kept short and last so it lands inside the "last 15 lines of the test
# log" that the harness prints into the job log on a failure.
# --------------------------------------------------------------------------

def tally(arm):
    rows = [r for r in records if r[1] == arm]
    sc = len([r for r in rows if [d for d in r[4] if d.lower().startswith("sc.exe")]])
    return sc, len([r for r in rows if r[4]]), len(rows)

skipped = len([r for r in records if r[1] == "skipped"])

summary = []
for arm in ARMS:
    sc, any_dump, total = tally(arm)
    if total:
        Debug.user("probe: RESULT %s %d/%d cycles wrote an sc.exe dump (%d/%d wrote any dump)"
                   % (arm, sc, total, any_dump, total))
        summary.append("%s %d/%d sc.exe" % (arm, sc, total))
Debug.user("probe: RESULT %d cycle(s) skipped, never reached the close" % skipped)
for cycle, arm, pids, gone, new in records:
    if new:
        Debug.user("probe: dump in cycle %d (%s): %s" % (cycle, arm, ",".join(new)))

# Fail on purpose so the harness prints the test log into the job log and stages
# the diagnostics. A probe branch has no passing verdict to give.
raise Exception("PROBE COMPLETE - %s, %d skipped" % (", ".join(summary), skipped))
