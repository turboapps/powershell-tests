# PROBE ONLY - DO NOT MERGE.
#
# A/B for the autodesk_dwgtrueview crash-dump failures (App Tests runs
# 34558812671 / 26.9.29, 34558810483 / 26.9.26, 34295107851 / 26.9.29). In all
# three the SikuliX script passed and the job was failed by the crash-dump gate:
# dwgviewr.exe died with c0000374 STATUS_HEAP_CORRUPTION, bucket
# HEAP_CORRUPTION_ACTIONABLE_BlockNotBusy_DOUBLE_FREE, on the app's own UI thread
# inside Autodesk's shutdown path -
#
#     AfxWinMain -> AcApAppImp::run -> AcApApp::terminate
#       -> AcRxImpDynamicLinker::unloadAllModules -> ::unloadModuleEx
#       -> acdbmgd!Terminate -> accoremgd!acrxEntryPoint -> coreclr!ThePreStub
#       -> JIT'd managed code -> mfc140u!CStringT::~CStringT -> free
#
# - freeing an MFC CString buffer that was already free. XVM is not in the
# failing frame: its RtlFreeHeap hook is a plain pass-through
# (mov [rsp+18h],r8 ; jmp ntdll!RtlFreeHeap+5) and the real ntdll free is what
# reports the block.
#
# Every crash landed at the SAME site - the close on line 49 of the production
# test, the only one immediately followed by `turbo stop test`. The step frames
# and the staged turbo client logs put the crash between the two:
#
#     Alt+F4 05:47:08 -> `turbo command: stop test` 05:47:10.4 -> dump 05:47:14
#     Alt+F4 04:04:22 -> `turbo command: stop test` 04:04:23.3 -> dump 04:04:26
#
# The Alt+F4 closes on lines 76 and 85, which no `turbo stop` follows, have never
# produced a dump. That is the hypothesis this probe tests, and it is the same
# mechanism already established for foxit: `turbo stop` WM_CLOSEs every top-level
# window and lands on an application that is already inside its own teardown.
#
# The probe runs the close many times in one job and alternates two arms that
# differ in exactly one thing - whether `turbo stop` overlaps the application's
# own shutdown:
#
#   stop-races  Alt+F4, then `turbo stop test` straight away. Production.
#   stop-after  Alt+F4, wait for dwgviewr.exe to leave the process list, THEN
#               `turbo stop test`. Measures the Alt+F4-only crash rate.
#
# Both arms are exercised in the same job, on the same pool VM, minutes apart, so
# a machine or load difference cannot land on one arm and not the other - the
# thing that made the earlier hec-ras sweep only suggestive.
#
# Cycle 1 is deliberately given to stop-after. It is the only launch with a cold
# merge-user profile (the one the privacy dialog appears on), so if the crash
# needs a first launch rather than the `turbo stop` overlap, the free hit goes to
# the arm the hypothesis says should be clean. Cycles 2..9 then alternate,
# starting with stop-races, so each arm also gets four warm launches.
#
# Nothing is deleted from the crash-dump directory: a --isolate=merge-user
# sandbox can virtualize a delete, which would leave the in-script tally and the
# gate's own list disagreeing. The probe only reads the directory, and records
# the live dwgviewr.exe PIDs per cycle so each dwgviewr.exe.<pid>.dmp the gate
# reports at the end can be attributed to the cycle - and therefore the arm -
# that produced it.

script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

import subprocess

setAutoWaitTimeout(60)
util.pre_test()

app_window = "Autodesk DWG TrueView"

# The launch the executor made before this script started (Test.ps1 TryTurboApp),
# repeated verbatim for every cycle after the first so each cycle closes the same
# kind of instance the production failures closed: a `turbo try` session named
# "test", not the Start Menu shortcut.
LAUNCH = ("turbo " + util.try_verb() + " autodesk/dwgtrueview --name=test"
          " --enable=disablefontpreload,usedllinjection,cachefileinfo"
          " --network=test --disable-proxy-resolve-via-proxy"
          " --using=turbobuild/isolate-edge-wc --isolate=merge-user -d"
          + util.read_extra())

# Where the workflow's "Enable crash dumps" step points WER LocalDumps for this
# job. The environment variable is what the workflow sets; the literal is the
# value it has had in every run and is the fallback for when the variable does
# not survive into the sikulixide container.
CRASH_DIR = os.environ.get("CRASH_DUMP_DIR") or "C:\\actions-runner\\_work\\_temp\\crashdumps"

WMCLOSE_PS1 = os.path.join(script_path, "wmclose.ps1")

CYCLES = 1

# Round-robin, so every arm gets three cycles per job under the same conditions.
# stop-after is dropped from the rotation: it has already been measured at 0/27
# across the first sweep and its only job now is as the cold-profile cycle 1.
ARMS = ["stop-races"]

# One cycle only, and no relaunch. This variant exists to be run with
# vm_diagnostics=true, where --diagnostic turns the launch verb into `run`
# (util.try_verb) and stopped sessions stay listed, so re-using --name=test
# across cycles could collide. One cycle is exactly the production shape - the
# cold first launch, Alt+F4, `turbo stop` - which is where every crash has landed
# anyway. The point is the VM log, not the count.

# --------------------------------------------------------------------------
# Probe helpers
# --------------------------------------------------------------------------

def dump_names():
    try:
        return sorted([f for f in os.listdir(CRASH_DIR) if f.lower().endswith(".dmp")])
    except (OSError, IOError):
        return []

def live_pids(image="dwgviewr.exe"):
    pids = []
    for line in run('tasklist /FI "IMAGENAME eq %s" /NH /FO CSV' % image).splitlines():
        fields = [f.strip().strip('"') for f in line.split('","')]
        if len(fields) >= 2 and fields[0].lower() == image.lower():
            pids.append(fields[1])
    return pids

def process_gone(image="dwgviewr.exe"):
    return not live_pids(image)

# Wait for the application's own exit to finish. Returns the seconds it took, or
# -1 if it never went away. A crash also takes the process off the list, so this
# returns on a crashed exit too - which is the point: the stop-after arm has to
# be able to record a crash of its own.
def wait_process_gone(image="dwgviewr.exe", max_wait=180, poll=2):
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

# Take the recorded dumps out of the folder before the next cycle.
#
# Two reasons, and neither is cosmetic. WER's DumpCount is 5: past that it
# REPLACES the oldest dump rather than declining to write, so over nine cycles
# the folder stops being a record of what crashed and the gate's closing list
# would name at most five. And a dwgviewr full dump is ~800 MB, so five of them
# is a 4 GB artifact upload on a job that otherwise uploads 300 MB.
#
# The per-cycle tally does not depend on this working. `new` is a diff against
# the listing this script last saw, and seen_dumps is re-read after the purge,
# so whether the delete really reaches the host or is virtualized away by the
# merge-user sandbox, each cycle's attribution is still computed against a
# consistent view. Log which it was: if the removals do not stick, the closing
# gate list is the one to read instead.
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

# Autodesk shows a modal "Privacy Settings" dialog on a first launch. It covers
# the Start tab and dims the window behind it, so app-loaded.png is only ever a
# washed-out near-match while it is up. Which launch it lands on depends on how
# much of the profile the merge-user sandbox carried over, so dismiss it wherever
# it appears rather than at one fixed point.
def dismiss_privacy_dialog():
    if exists("privacy-dialog.png", 1):
        click("privacy-ok.png")
        wait(2)
        return True
    return False

# Returns True once the Start tab is up, False if it never arrived.
#
# It returns rather than raises because a probe that dies on the first launch it
# cannot read throws away every cycle after it. Probe run 34626264320 did exactly
# that: cycles 1-4 measured cleanly, cycle 4 crashed, and cycle 5 ended the run
# with four cycles unmeasured.
#
# Do not read the FindFailed that ended that run as a dimmed window. It reported
# "app-loaded.png: (109x51) seen at (32, 123) with 0.92", which is the score the
# production test's own comment attributes to the privacy dialog dimming the
# Start tab - but the FAILED step frame is a bare desktop with no DWG TrueView on
# it at all. The "seen at ... with" clause is SikuliX's stale lastSeen hint, not
# a current match, so it described an earlier cycle. The app simply never came
# up; see the retry in the cycle loop for what actually goes wrong there.
#
# blind_esc: after the app has had a fair chance to load, dismiss whatever is
# there, in case a launch does one day come up behind a dialog this probe holds
# no reference for. ESC is sent late and slowly so it cannot race a normal load.
def wait_app_loaded(timeout=110, blind_esc=75):
    started = time.time()
    while time.time() - started < timeout:
        if dismiss_privacy_dialog():
            continue
        if exists("app-loaded.png", 2):
            # Focus the main window rather than clicking app-loaded.png: that
            # image is the wordmark inside the Start tab's embedded browser pane,
            # and clicking it leaves focus in the pane, where the app's
            # accelerators are swallowed.
            util.activate_app_window(app_window, 10)
            wait(10)
            return True
        if time.time() - started > blind_esc:
            util.activate_app_window(app_window, 2)
            type(Key.ESC)
            wait(3)
    Debug.user("probe: app-loaded.png never appeared in %d s" % timeout)
    return False

# Put the machine back where cycle 1 found it, whatever the cycle left behind: a
# dialog nothing dismissed, an instance that never finished loading, a container
# still up. taskkill terminates rather than faulting, so nothing here can write a
# dump of its own and inflate the next cycle's count.
def reset_between_cycles():
    type(Key.ESC)
    wait(1)
    run("turbo stop test")
    for image in ("dwgviewr.exe", "AcHelp2.exe", "ADPClientService.exe",
                  "AdskAccessService.exe"):
        os.system('cmd /c taskkill /f /im "%s" /t' % image)
    wait(5)

def launch():
    # Leave no session behind for the new one to collide with. Unconditional: a
    # stop with nothing to stop is a no-op, and asking `turbo sessions -l` first
    # would answer about the latest session, which after a cycle's own stop is
    # the sikulixide container running this script - always Running, so the
    # check would misfire anyway. Outside the measured window on purpose: by
    # here the previous cycle's close is long finished, so this stop can never
    # be the one that races a teardown.
    run("turbo stop test")
    wait(5)
    subprocess.Popen(LAUNCH)
    wait(10)

# --------------------------------------------------------------------------
# The two arms. They differ in one line.
# --------------------------------------------------------------------------

def close_stop_races():
    type(Key.F4, Key.ALT)
    run("turbo stop test")
    return None

def close_stop_after():
    type(Key.F4, Key.ALT)
    gone = wait_process_gone()
    run("turbo stop test")
    return gone

# Alt+F4, then the VM's WM_CLOSE broadcast and nothing else.
#
# wmclose.ps1 does what TerminateSelfGracefullyCallback's window half does -
# EnumWindows, filter to the process, PostMessageW(WM_CLOSE) to every top-level
# window - but from the host, with no `turbo stop`, no CTRL_CLOSE_EVENT, no
# container teardown and no TerminateProcess timer. The 2 s pause matches the gap
# the production failures had between the Alt+F4 and `turbo stop` reaching the
# process (1.3 s and 2.3 s in the two runs with client logs).
#
# Crashes here and not only under stop-races => the broadcast alone is enough and
# the VM contributes nothing but the message. Clean here while stop-races crashes
# => something else in the stop is required, and the window broadcast is not the
# mechanism.
# PostMessage returns as soon as the message is queued, and `turbo stop` does not
# - run() blocks for the ~10 s the stop takes, by which time a crash 4 s in has
# long happened. So this arm has to wait for the outcome itself, or settle_dumps
# could start looking before the app has even finished dying.
def close_wmclose_storm():
    type(Key.F4, Key.ALT)
    wait(2)
    out = run('powershell -NoProfile -ExecutionPolicy Bypass -File "%s"' % WMCLOSE_PS1)
    Debug.user("probe: %s" % out.strip().replace("\n", " | "))
    return wait_process_gone()

# `turbo stop` against an app that is NOT already closing.
#
# The other arms all put the app into its own teardown first. If the crash needs
# that overlap, this is clean; if `turbo stop` crashes a settled, idle app on its
# own, the overlap is not the mechanism and the VM's stop path is doing more than
# delivering a close.
def close_stop_only():
    run("turbo stop test")
    return wait_process_gone()

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
    # launches its own so it closes the same kind of session.
    #
    # Retry once through a full reset. A launch that follows a crashed cycle can
    # come up with nothing on screen at all: in probe run 34626264320 cycle 4
    # crashed, cycle 5's `turbo try` returned 0 and detached its session, and the
    # desktop stayed bare for the whole 180 s wait. The crashed instance leaves
    # Autodesk's helper processes behind and the next dwgviewr finds them, so the
    # reset that clears them is what makes the retry worth making - without it a
    # retry would just fail the same way.
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
    elif arm == "wmclose-storm":
        gone = close_wmclose_storm()
    elif arm == "stop-only":
        gone = close_stop_only()
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
    return len([r for r in rows if r[4]]), len(rows)

skipped = len([r for r in records if r[1] == "skipped"])

summary = []
for arm in ARMS + ["stop-after"]:
    crashed, total = tally(arm)
    if total:
        Debug.user("probe: RESULT %s %d/%d cycles crashed" % (arm, crashed, total))
        summary.append("%s %d/%d" % (arm, crashed, total))
Debug.user("probe: RESULT %d cycle(s) skipped, never reached the close" % skipped)
for cycle, arm, pids, gone, new in records:
    if new:
        Debug.user("probe: dump in cycle %d (%s): %s" % (cycle, arm, ",".join(new)))

# Fail on purpose so the harness prints the test log into the job log and stages
# the diagnostics. A probe branch has no passing verdict to give.
raise Exception("PROBE COMPLETE - %s, %d skipped" % (", ".join(summary), skipped))
