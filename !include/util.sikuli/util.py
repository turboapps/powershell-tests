# Common operations used in app test scripts.
from sikuli import *
import re
import shutil
import time
from java.io import File
from java.awt.image import BufferedImage
from javax.imageio import ImageIO

# Useful paths.
desktop = os.path.join((os.environ["USERPROFILE"]), "Desktop")
start_menu = os.path.join((os.environ["APPDATA"]), "Microsoft", "Windows", "Start Menu", "Programs")

# ---------------------------------------------------------------------------
# Per-step screenshots
# ---------------------------------------------------------------------------
# The SikuliX log records actions, not what the screen looked like, and the CI
# harness's only screenshot is taken after the test has torn everything down.
# So a passing run leaves nothing to compare a later failure against, and a
# failure shows the desktop after SikuliX gave up rather than the screen it
# gave up on. pre_test() therefore wraps the action functions (click, type,
# wait, ...) in the calling test's namespace, and in util's own, so that every
# action first saves a JPEG of the whole screen:
#
#     <Desktop>\<app>-steps\NNN-<action>-<target>.jpg   before each action
#     <Desktop>\<app>-steps\NNN-FAILED-<action>-<target>.jpg   when it raises
#
# <target> is the reference image's base name, so a frame reads as
# "007-click-zip_add". Desktop writes are host-visible under the harness's
# --isolate=merge-user (that is how the test log gets out too), and the CI
# harness (applab Invoke-AppTest.ps1) stages the folder into the
# <app>-diagnostics artifact on every verdict.
#
# Frames are JPEG (a PNG of a 1080p desktop is several MB; a JPEG is a few
# hundred KB) and capped per run. A repeat of the same action on the same
# target within a couple of seconds - an exists() polling loop - is not saved
# again; distinct steps always are, however fast they follow each other (a
# time-based limit was tried first and dropped the click after every instant
# type(Key.ENTER)). Capture is best-effort throughout: a failure to save a
# frame is logged once via Debug.user and never fails the test.

_STEP_ACTIONS = ("click", "doubleClick", "rightClick", "hover", "dragDrop",
                 "type", "paste", "wait", "exists", "find")
_STEP_REPEAT_INTERVAL = 2.0   # seconds before the same action+target is saved again
_STEP_MAX_FRAMES = 300        # hard cap per run; the FAILED frame is exempt
_step_state = {"dir": None, "n": 0, "last": 0.0, "tag": None, "warned": False}

# <Desktop>\<app>-steps, with <app> = the test's folder name (<app>\test.sikuli\test.py),
# which is the CI matrix name the harness stages by.
def _step_dir():
    if _step_state["dir"] is None:
        script = os.path.abspath(sys.argv[0])
        app = os.path.basename(os.path.dirname(os.path.dirname(script)))
        folder = os.path.join(desktop, app + "-steps")
        if not os.path.isdir(folder):
            os.makedirs(folder)
        _step_state["dir"] = folder
    return _step_state["dir"]

# Name fragment for an action's target: reference image base name for a string
# or Pattern, the class name for a Region/Location/Match, None for text/keys.
def _step_label(target):
    if isinstance(target, basestring):
        if target.lower().endswith((".png", ".jpg")):
            return os.path.splitext(os.path.basename(target))[0]
        return None
    try:
        name = target.getFilename()
        if name:
            return os.path.splitext(os.path.basename(name))[0]
    except:
        pass
    return target.__class__.__name__.lower()

# Save one JPEG frame of the whole screen. Never raises.
def _step_capture(tag):
    try:
        failed = tag.startswith("FAILED")
        now = time.time()
        if not failed:
            if tag == _step_state["tag"] and now - _step_state["last"] < _STEP_REPEAT_INTERVAL:
                return
            if _step_state["n"] >= _STEP_MAX_FRAMES:
                if not _step_state["warned"]:
                    _step_state["warned"] = True
                    Debug.user("step screenshots: cap of %d frames reached, not saving more" % _STEP_MAX_FRAMES)
                return
        _step_state["n"] += 1
        _step_state["last"] = now
        _step_state["tag"] = tag
        safe = re.sub(r"[^A-Za-z0-9._-]+", "_", tag)[:80]
        path = os.path.join(_step_dir(), "%03d-%s.jpg" % (_step_state["n"], safe))
        # The JPEG writer rejects an image with an alpha channel; redraw as RGB.
        img = SCREEN.capture().getImage()
        rgb = BufferedImage(img.getWidth(), img.getHeight(), BufferedImage.TYPE_INT_RGB)
        g = rgb.createGraphics()
        g.drawImage(img, 0, 0, None)
        g.dispose()
        ImageIO.write(rgb, "jpg", File(path))
    except:
        if not _step_state["warned"]:
            _step_state["warned"] = True
            Debug.user("step screenshots: capture failed, frames may be missing: %s" % sys.exc_info()[1])

def _step_wrap(name, original):
    def wrapped(*args, **kwargs):
        target = args[0] if args else None
        # wait(3) / exists(2): a plain timeout, nothing on screen to name.
        skip = name in ("wait", "exists", "find") and isinstance(target, (int, long, float))
        label = None if skip else _step_label(target)
        tag = name if label is None else name + "-" + label
        if not skip:
            _step_capture(tag)
        try:
            return original(*args, **kwargs)
        except:
            # The screen at the moment the action gave up (FindFailed, focus
            # error, ...): the frame a failure investigation starts from.
            _step_capture("FAILED-" + tag)
            raise
    wrapped._step_original = original
    wrapped.__name__ = name
    return wrapped

# Replace the action functions in each namespace with capturing wrappers.
# Idempotent: re-installing (tests call reload(util)) unwraps first, so a
# function is never wrapped twice.
def _install_step_hooks(namespaces):
    for ns in namespaces:
        for name in _STEP_ACTIONS:
            fn = ns.get(name)
            if fn is None:
                continue
            original = getattr(fn, "_step_original", None) or fn
            ns[name] = _step_wrap(name, original)

# Operations before running app test.
def pre_test(no_min=False):
    # Per-step screenshots for the calling test and for util's own helpers.
    # Installed here rather than at import: every test does import + reload(util)
    # + pre_test(), and the caller's namespace is only known from the call.
    try:
        _install_step_hooks([sys._getframe(1).f_globals, globals()])
    except:
        Debug.user("step screenshots: hook install failed, no frames this run: %s" % sys.exc_info()[1])

    # Workaround for the bug that when Num-Lock is on, Key.SHIFT does not work with arrow keys: https://answers.launchpad.net/sikuli/+question/143874.
    if Env.isLockOn(Key.NUM_LOCK):
        type(Key.NUM_LOCK)

    # OneDrive shortcut should not be captured.
    assert(not os.path.exists(os.path.join(start_menu, "OneDrive (2).lnk")))

# Get credentials from secrets.txt. That secret file locates under the "resources" folder of the app script folder.
def get_credentials(path):
    credentials = {}
 
    with open(path, "r") as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split(",")
            credentials[key] = value

    return credentials

# Launch Adobe Creative Cloud
def launch_adobe_cc(username, password):
    run('turbo installi creativeclouddesktop --network=test --enable=usedllinjection --isolate=merge --offline')
    run("explorer " + get_shortcut_path_by_prefix(start_menu, "Adobe Creative Cloud"))
    activate_app_window("Creative Cloud Desktop",30)
    adobe_cc_login(username, password)
    wait(15)
    type("w", Key.CTRL)
    wait(5)
    closeApp("Creative Cloud Desktop")

# Log in for Adobe Creative Cloud.
def adobe_cc_login(username, password):
    wait(Pattern("adobe_login.png").similar(0.40),60)
    click("cancel-button.png")
    wait(20)
    wait(Pattern("adobe_login.png").similar(0.40),10)
    click(Pattern("adobe_login.png").similar(0.40))
    wait(3)
    paste(username)
    wait(3)
    type(Key.ENTER)
    # Wait for the password page itself, not for anything shaped like a text
    # field. The email page and the password page are the same shape - a label
    # over a rounded input box - so the old reference (a "Password" crop matched
    # at similar(0.40)) also matched the EMAIL field, at 0.42-0.50. That made
    # this wait return immediately on the very page it was meant to wait past,
    # leaving the fixed wait(3) below as the only thing between the email box
    # and paste(password): when Adobe's page took longer than that to navigate,
    # the password went in after the email address, the sign-in failed, and the
    # test died many steps later on an unrelated image of whatever the app shows
    # when it is not signed in - with the password in cleartext in the
    # diagnostics artifact. The reference is now the "Continue with password"
    # label of the current page, which scores 0.98-1.00 there and 0.47-0.55 on
    # the email page, so the default similarity separates the two and this is a
    # real wait. Re-capture it if Adobe relabels the page: a stale reference is
    # what forced the 0.40 in the first place. The offset clicks into the field
    # below the label.
    wait("adobe_login_pass.png",60)
    wait(1)
    click(Pattern("adobe_login_pass.png").targetOffset(0,27))
    wait(3)
    paste(password)
    wait(3)
    type(Key.ENTER)
    # Fail at the cause, not 30 steps downstream: a sign-in that worked leaves
    # the password page, a sign-in that did not keeps it up (with an error).
    if not waitVanish("adobe_login_pass.png",60):
        raise FindFailed("adobe_cc_login: sign-in did not complete, the password page is still up")
    if exists("adobe_login_signout_others.png",15):
        click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
        click(Pattern("adobe_login_continue.png").similar(0.80))
    if exists("adobe_login_team.png"):
        click(Pattern("adobe_login_continue.png").similar(0.80))

# Get the path of the shortcut for the apps that have different shortcut names for different versions.
# Assume there is only one match inside the folder.
def get_shortcut_path_by_prefix(folder_path, prefix):
    files = os.listdir(folder_path)
    matching = [file for file in files if file.startswith(prefix)]
    return os.path.join(folder_path, matching[0])

# Launch an app from its installed shortcut, given every name it is known by.
#
# Two naming schemes are in play, and which one applies depends on the image,
# not on the test. When the captured installer created Start Menu shortcuts of
# its own (any MSI/EXE app), the client replays those, so the shortcut keeps
# the vendor's name and subfolder ("Zoom\Zoom Workplace.lnk"). When the
# installer created none (a ZIP app such as Temurin), the client synthesizes a
# single flat shortcut from the image Title ("Temurin JDK LTS ARM64.lnk").
# Passing both candidates keeps a test working under either, and across a
# rebuild that changes which one an image produces.
#
# Each candidate is relative to `base` (the Start Menu by default): a string
# for a flat shortcut, or a list of segments for one inside a subfolder.
#
# Resolve before launching, because run("explorer <missing path>") does not
# fail - Explorer silently opens a "Documents" window and the test dies later
# at an unrelated wait(), pointing at the wrong thing. Raise here instead, and
# list what is actually installed so the real name is in the log.
def launch_shortcut(*candidates, **kwargs):
    base = kwargs.get("base", start_menu)
    tried = []
    for candidate in candidates:
        parts = list(candidate) if isinstance(candidate, (list, tuple)) else [candidate]
        path = os.path.join(base, *parts)
        tried.append(path)
        if os.path.exists(path):
            run("explorer " + path)
            return path
    raise AssertionError(
        "No shortcut found for this app.\nTried:\n  %s\nInstalled under %s:\n  %s"
        % ("\n  ".join(tried), base, "\n  ".join(list_shortcuts(base)) or "(nothing)"))

# List the shortcuts under a folder, two levels deep, relative to it.
# Used to report what is really installed when launch_shortcut finds nothing.
def list_shortcuts(base):
    found = []
    if not os.path.exists(base):
        return found
    for entry in sorted(os.listdir(base)):
        full = os.path.join(base, entry)
        if os.path.isdir(full):
            for child in sorted(os.listdir(full)):
                found.append(os.path.join(entry, child))
        else:
            found.append(entry)
    return found

# Given a partial file name and path find the file and return the path.
# Useful for searching for a shortcut that changes names eg. PowerBI RS.
def find_file(folder_path, partial_name):
    # Check if the folder path exists.
    if not os.path.exists(folder_path):
        return None   
    # Iterate over files in the folder.
    for file_name in os.listdir(folder_path):
        # Check if the partial name is in the file name.
        if partial_name in file_name:
            # Return the full path of the first matching file.
            return os.path.join(folder_path, file_name) 
    # If no matching file is found, return None.
    return None

# Check if a file exists. It checks every 10 seconds unitl `try_limit` is reached.
def file_exists(path, try_limit):
    tried = 0
    while tried < try_limit:
        if os.path.exists(path):
            return True
        tried += 1
        time.sleep(10)
    return False

# Activate app window named (windowName) - will attempt for (numAttempts) seconds
def activate_app_window(windowName, numAttempts):
    for attempt in range(numAttempts):
        app_window = App().focus(windowName)
        if app_window.isValid():
            return True
        else:
            wait(1)

# Close the Windows firewall alert prompt.
def close_firewall_alert(wait_time = 200):
    activate_app_window("Windows Security Alert", wait_time)
    wait("firewall.png")
    click(Pattern("firewall.png").targetOffset(95,29))
# Close the Windows firewall alert prompt. Continue if not prompted after 60 seconds.
def close_firewall_alert_continue(wait_time = 200):
    activate_app_window("Windows Security Alert", wait_time)
    if exists("firewall.png"):
        click(Pattern("firewall.png").targetOffset(95,29))

# Extra turbo flags the CI harness passed to executor.ps1 as -extra (e.g.
# "--vm=<xvm> --diagnostic"). PrepareTest writes them to <app>\extra.txt so a
# test that launches turbo itself - from a Command Prompt or a subprocess rather
# than through Test.ps1's TryTurboApp/RunTurboApp - can append them to its own
# command line:
#
#     type("turbo try trillian --offline --name=trytrillian -d" + util.read_extra())
#
# Returns "" when there is no file or it is empty, otherwise the flags with a
# leading space so the call above needs no separator.
def read_extra():
    script = os.path.abspath(sys.argv[0])
    path = os.path.join(os.path.dirname(os.path.dirname(script)), "extra.txt")
    try:
        with open(path) as f:
            extra = f.read().strip()
    except IOError:
        return ""
    return (" " + extra) if extra else ""

# "try" or "run" for a launch the test issues itself. `turbo try` removes the
# session - sandbox and VM logs included - as soon as it ends, so on a diagnostic
# run (--diagnostic in the harness's -extra) the launch is made with `run` and
# the session persists until the next PrepareTest's `turbo rm -a`. Mirrors
# Test.ps1's TryTurboApp:
#
#     subprocess.Popen("turbo " + util.try_verb() + " ffmpeg/ffmpeg -n=test ..." + util.read_extra())
def try_verb():
    return "run" if "--diagnostic" in read_extra().split() else "try"

# Assert that the named session has ended. A `try` session is removed from
# `turbo sessions` when it ends; a `run` session (what a diagnostic run uses, see
# try_verb) stays listed as stopped. Either counts as ended; a session still
# listed as Running does not.
def check_stopped(name="test"):
    for line in run("turbo sessions").splitlines():
        if name in line.split():
            assert "Running" not in line, "session %s is still running: %s" % (name, line.strip())
            return

# Check if the most recently created Turbo session is terminated.
# It is usually the session for the app to be tested.
#
# A container goes away only once its last process has exited, so an app that
# leaves a helper behind after its window closes keeps the session Running long
# after the test is finished with it. On the runs that pass, the session is
# already gone at the first poll, so the assertion on its own says nothing about
# how close a failing run came: record how long the wait actually took, and what
# `turbo sessions -l` still listed when the budget ran out.
def check_running(max_retries=12, delay=5):
    for attempt in range(max_retries):
        output = run("turbo sessions -l")
        if "Running" not in output:
            if attempt:
                Debug.user("check_running: the session went away after %d s" % (attempt * delay))
            # The session has ended: its VM logs are complete and about to be
            # wiped if the test launches the app again, so copy them out now.
            collect_vm_logs()
            return
        time.sleep(delay)
    Debug.user("check_running: still Running after %d s\n%s" % (max_retries * delay, output))
    assert "Running" not in output

# Give the most recently created session a bounded chance to end on its own,
# then stop it and assert that the stop worked.
#
# Some apps close their window and leave their process tree behind: Acrobat
# Reader keeps AcroRd32, the AcroCEF sign-in/AI hosts and AdobeCollabSync alive
# for minutes after Ctrl+Q (App Tests 34097578991: still Running after 180 s;
# the 09-06 diagnostic run's VM log showed every process alive 366 s later,
# with new RdrCEF renderers still spawning). On the runs that pass the session
# is gone at the first poll, so the outcome is bimodal and no wait is long
# enough to be safe. That is the app's behaviour, not the product's, so record
# it and move on: after `grace` seconds stop the session ourselves and check
# that the container can be torn down - which is the part that is Turbo's job.
#
# paintdotnet and azuredatastudio already stop their session before
# check_running(); this does the same, but only when the app has not exited by
# itself, so a clean quit still shows up as one in the log.
#
# The session is stopped by id, never with `turbo stop -a`: the sikulixide
# container running this very script is a session too.
def end_session(grace=60, delay=5):
    started = time.time()
    while True:
        output = run("turbo sessions -l")
        if "Running" not in output:
            Debug.user("end_session: the session exited on its own after %d s" % int(time.time() - started))
            collect_vm_logs()
            return True
        if time.time() - started >= grace:
            break
        time.sleep(delay)
    session = _latest_session_id()
    Debug.user("end_session: still Running after %d s, stopping %s\n%s" % (grace, session or "?", output))
    if not session:
        # Nothing to address the stop to; fall through to the assertion so the
        # listing above is what the failure reports.
        assert "Running" not in output
    run("turbo stop " + session)
    check_running()
    return False

# Id of the most recently created session: the full id from `turbo sessions -l
# --format=json`, falling back to the first column of the plain listing (an
# 8-hex prefix, which `turbo stop` also resolves). None if neither yields one.
#
# SikuliX's run() returns the command's exit code as its own first line and the
# output after it, so the JSON has to be found inside that text - json.loads()
# on the whole string always throws. Probe run 34279763399 exercised this path
# and caught exactly that: it fell through to the 8-hex prefix every time, and
# the JSON branch was dead code that only cost an extra `turbo sessions -l`.
def _latest_session_id():
    try:
        import json
        raw = run("turbo sessions -l --format=json")
        start = raw.find("[")
        if start >= 0:
            containers = json.loads(raw[start:])[0]["result"]["containers"]
            if containers:
                return containers[0]["id"]
    except:
        pass
    for line in run("turbo sessions -l").splitlines():
        token = line.split(None, 1)[0] if line.strip() else ""
        if re.match(r"^[0-9a-f]{8,}$", token):
            return token
    return None

# Turbo VM logs.
#
# A container started with --diagnostic writes its VM diagnostic log to
# <sandbox>\logs\xclog_0x<pid>.txt. The client deletes and recreates that folder
# every time the same container starts again (a relaunch from the installed
# shortcut, a file-association check), so a launch's logs survive only if they
# are copied out before the next launch. They are copied at the points where a
# session is known to have ended, not by polling: here from check_running(), and
# by Test.ps1's CollectVmLogs after the sikulix test returned (which also covers
# a failure, where the session is usually still running). Both write the same
# layout, <Desktop>\<app>-vm-logs\<container id>\<logs tree>, which the CI
# harness (applab Invoke-AppTest.ps1) stages as the <app>-vm-logs artifact.
#
# Only sandboxes holding an xclog_* file are copied, so on a run without
# --diagnostic this costs one directory listing. An existing copy is overwritten
# when the source is the same file grown (same first bytes, not smaller) and kept
# as <name>.1, .2, ... when a different file has reappeared under the same name
# (pid reuse across launches). Best-effort: never fails the test.
_vm_logs_state = {"root": None}

def collect_vm_logs():
    try:
        root = _vm_logs_sandbox_root()
        if not os.path.isdir(root):
            return
        script = os.path.abspath(sys.argv[0])
        app = os.path.basename(os.path.dirname(os.path.dirname(script)))
        dest_root = os.path.join(desktop, app + "-vm-logs")
        for cid in os.listdir(root):
            logs = os.path.join(root, cid, "logs")
            if not os.path.isdir(logs):
                continue
            if not [f for f in os.listdir(logs) if f.lower().startswith("xclog_")]:
                continue
            for dirpath, dirnames, filenames in os.walk(logs):
                rel = os.path.relpath(dirpath, logs)
                for name in filenames:
                    src = os.path.join(dirpath, name)
                    dst = os.path.normpath(os.path.join(dest_root, cid, rel, name))
                    try:
                        _vm_logs_copy(src, dst)
                    except:
                        Debug.user("vm logs: %s not copied: %s" % (src, sys.exc_info()[1]))
    except:
        Debug.user("vm logs: collection failed: %s" % sys.exc_info()[1])

# The sandbox root the client is using, resolved once per run. `turbo config
# --reset` in PrepareTest leaves the default location; a relocated storage path
# is honoured when the client reports one.
def _vm_logs_sandbox_root():
    if _vm_logs_state["root"] is None:
        root = os.path.join(os.environ["LOCALAPPDATA"], "Turbo", "Containers", "sandboxes")
        try:
            import json
            cfg = json.loads(run("turbo config --format=json"))[0]["result"]["configuration"]
            if cfg.get("containerStoragePath"):
                root = os.path.expandvars(cfg["containerStoragePath"])
        except:
            pass
        _vm_logs_state["root"] = root
    return _vm_logs_state["root"]

def _vm_logs_copy(src, dst):
    if os.path.exists(dst):
        src_len = os.path.getsize(src)
        dst_len = os.path.getsize(dst)
        if src_len < dst_len or not _vm_logs_same_head(src, dst, dst_len):
            n = 1
            while os.path.exists("%s.%d" % (dst, n)):
                n += 1
            os.rename(dst, "%s.%d" % (dst, n))
        elif src_len == dst_len:
            return
    d = os.path.dirname(dst)
    if not os.path.isdir(d):
        os.makedirs(d)
    shutil.copyfile(src, dst)

# True when the first min(512, length) bytes of both files match: the same log
# file (grown or unchanged) rather than a new launch's log under a reused name.
def _vm_logs_same_head(a, b, length):
    n = min(512, length)
    if n <= 0:
        return True
    with open(a, "rb") as fa:
        ha = fa.read(n)
    with open(b, "rb") as fb:
        hb = fb.read(n)
    return ha == hb

# Close an application by window name.
#
# SikuliX's App.close() intermittently raises IndexOutOfBoundsException when its
# internal application list is momentarily empty. That fails the test even though
# the application is running and was about to be closed anyway: it hit
# goto_gotoconnect and both tableau tests in App Tests run 33676687141, each time
# right after a help link had opened the browser, and powerbi before that. Fall
# back to taskkill for the browsers, which a test only ever closes as cleanup and
# which are safe to force-close.
_EXECUTABLES = {
    "edge": "msedge.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
}

def close_app(name):
    try:
        closeApp(name)
    except:
        executable = _EXECUTABLES.get(name.lower())
        if executable:
            run("taskkill /F /IM " + executable)

# Wait for an app to be really gone before launching it again.
#
# A quit keystroke returns as soon as the app accepts it, and the window leaves
# the screen and the taskbar well before the process tree does. Relaunching into
# that gap finds an instance that still holds its single-instance lock but can no
# longer answer, and Firefox answers with "Firefox is already running, but is not
# responding" instead of opening the page. In App Tests run 34097555049 the
# protocol launch went out 2 s after Ctrl+Shift+Q -- step frames 031 and 032 are
# both a Firefox-less desktop -- and the wait that followed timed out against
# that dialog.
#
# Both halves have to be quiet, because measured on the pool VMs they go quiet in
# either order: a probe over three runs saw the session still Running 6 s after
# the process had gone, and the process still alive while the session had already
# ended. The lock that produces the dialog belongs to the process, and the
# container teardown belongs to the session, so neither on its own is the answer.
# Both-quiet took 0-8 s across six measurements, so the default bound is well
# clear of it.
#
# Unlike check_running, which is the end-of-test assertion, this is a mid-test
# settle: an app that outlasts the bound is being slow, which is worth a log line
# and not worth failing a test that has not tested anything yet.
def wait_app_quiet(executable, max_wait=60, poll=2):
    waited = 0
    while waited <= max_wait:
        session_busy = "Running" in run("turbo sessions -l")
        process_busy = executable in run('tasklist /FI "IMAGENAME eq ' + executable + '"')
        if not session_busy and not process_busy:
            if waited:
                Debug.user("wait_app_quiet: %s went quiet after %d s" % (executable, waited))
            return True
        wait(poll)
        waited += poll
    Debug.user("wait_app_quiet: %s still had a session or a process after %d s" % (executable, max_wait))
    return False

# Paste text without racing the next clipboard write.
#
# SikuliX's paste() puts the text on the clipboard and sends Ctrl+V, then returns
# without waiting for the target application to read it. Keystrokes are queued and
# drained by the application at its own pace, while the clipboard write is
# immediate and out of band, so a following paste() can replace the clipboard
# while the previous Ctrl+V is still unprocessed and both pastes then insert the
# same string. In App Tests run 33890588162 the PowerPoint bullets came out
# "First line" / "Third line" / "Third line" and the run failed three steps later
# at an image the wrong text could never match, pointing at the wrong step.
#
# Hold after the paste so the application has drained the clipboard before the
# next call moves it on. Do not read the clipboard back to confirm the write:
# reading it from inside the sikulixide container leaves the application's
# container pasting nothing at all (verified on os-test2, where the Office
# sign-in field came up empty on every attempt).
def paste_text(text, settle=1):
    paste(text)
    wait(settle)

# Put a path into a Windows file dialog's "File name" field, leaving it there
# for the caller to confirm.
#
# wait(field_image) only proves the dialog is painted, not that it owns the
# keyboard. In App Tests run 33849047386 (videolan_vlc-x64) the first chord sent
# to the freshly opened Open dialog lost its modifier: paste()'s Ctrl+V arrived
# as a bare "v", which the dialog took for the whole file name. So click the
# field first, which both settles the dialog and puts the caret in it, and clear
# whatever a stray keystroke may already have typed before pasting.
#
# field_image is the "File name:" label; the click reaches past it into the
# field itself.
def paste_path_in_dialog(field_image, path):
    click(Pattern(field_image).targetOffset(40, 0))
    wait(0.5)
    type("a", Key.CTRL)
    paste_text(path)

# Put a path into a Windows file dialog's "File name" field and confirm it.
#
# Pastes as paste_path_in_dialog does, then confirms and retries if the dialog
# rejects the name -- which is how a dropped modifier showed itself in run
# 33849047386: Enter raised "v - File not found" and the test died three lines
# later at an image the wrong file could never match. The error box is checked
# for only briefly because VLC's title overlay, which the next wait() matches,
# is on screen for just a few seconds after playback starts.
def open_file_in_dialog(field_image, path, error_image="file_not_found.png", attempts=3):
    for attempt in range(attempts):
        paste_path_in_dialog(field_image, path)
        type(Key.ENTER)
        if not exists(error_image, 1):
            return True
        Debug.user("open_file_in_dialog: dialog rejected the path on attempt %d of %d" % (attempt + 1, attempts))
        type(Key.ENTER)  # OK is the default button of the "File not found" box
        wait(1)
    raise FindFailed("open_file_in_dialog: the dialog rejected '%s' %d times" % (path, attempts))

# Save the page a browser is showing as "Web Page, HTML only" through its
# Save As dialog, and prove the file landed.
#
# A Save As dialog gives a dropped modifier nowhere to show itself. The field
# opens with the app's suggested name selected, so a paste() whose Ctrl is lost
# types a bare "v" over it and the page saves as "v.htm" in whatever folder the
# dialog happens to be showing -- no error box, no failed match, the save
# genuinely succeeds under the wrong name in the wrong place. In App Tests run
# 34295135821 (mozilla_firefox) it went to Downloads\v.htm and the test spent
# 200 s in file_exists waiting for a Desktop file that was never going to
# appear, then died on a bare assert that said nothing about why.
#
# So paste through paste_path_in_dialog, and then check the outcome rather than
# trusting it: if the intended file is not there, the name did not go in, and
# reopening the dialog and redoing the save is the only thing that can help.
# Escape first on a retry to clear the download panel the wrong save popped up,
# which would otherwise swallow the Ctrl+S.
#
# The type only needs setting on the first attempt. A reopened Save As dialog
# comes up on the type it was last used with -- probe frame 019 for run
# 34295135821 shows the retry's dialog already on "Web Page, HTML only" -- so a
# retry inherits the right type and must leave the list alone. Stepping into it
# again is what broke the first cut of this retry: Down is relative, so from the
# remembered entry it landed on "Text Files" and attempt 2 saved a .txt. Picking
# the entry by image instead is no better; the wanted row matches at 0.757 when
# the list opens elsewhere, and the already-selected row is drawn highlighted
# and does not match at all.
def save_page_as_html(field_image, type_image, path, result_path, attempts=3):
    for attempt in range(attempts):
        if attempt:
            type(Key.ESC)
            wait(1)
        type("s", Key.CTRL)
        wait(field_image)
        paste_path_in_dialog(field_image, path)
        if attempt == 0:
            click(Pattern(type_image).targetOffset(39, 1))
            wait(2)
            type(Key.DOWN)   # "Web Page, complete" -> "Web Page, HTML only"
            wait(2)
            type(Key.ENTER)  # commit the file type
            wait(2)
        type(Key.ENTER)      # Save
        if file_exists(result_path, 2):
            return True
        Debug.user("save_page_as_html: '%s' was not written on attempt %d of %d" % (result_path, attempt + 1, attempts))
    raise FindFailed("save_page_as_html: '%s' was never written in %d attempts" % (result_path, attempts))

# Bring a window to the front and wait for something on it, re-asserting the
# focus between polls.
#
# App().focus(name) is not reliable on its own, and it reports nothing when it
# fails. In App Tests runs 34090380526..34090412066 (ggerganov_llama-cpp) a
# single App("conhost").focus() on a minimized console restored nothing and the
# wait that followed timed out against a bare desktop -- indistinguishable, from
# the log, from the window being up but the content not printed yet. So poll
# instead of trusting one call, and re-focus each round in case another window
# takes the foreground back.
#
# Returns True as soon as the image is found, False if it never appears; the
# caller decides whether that is fatal.
def focus_and_wait(window, image, attempts=30, poll=10):
    for attempt in range(attempts):
        App(window).focus()
        if exists(image, poll):
            return True
    Debug.user("focus_and_wait: %s not found on '%s' after %d attempts" % (image, window, attempts))
    return False

# Drive a browser to a URL through its address bar, and prove it got there.
#
# Alt+D, the paste and Enter only reach the browser if the browser still holds
# the foreground when they are sent, and a container the test launched moments
# earlier can take it away. In App Tests run 34398082628 (opensearch_opensearch)
# the curl container's console -- started one line earlier as
#   turbo try base -n=curl ... --startup-file=cmd -- /C put.bat
# -- raised itself *after* App().focus("Edge") and covered Edge's address bar,
# so all three went to cmd.exe instead. Step frame 005 catches it mid-paste with
# that console, titled "cmd.exe @curl#0cd0d95f", on top and focused; the FAILED
# frame four lines later still shows the address bar on the previous URL.
# Padding the wait() before the focus cannot fix that -- the console's timing is
# the thing that varies -- so re-assert the focus each round and check the
# outcome instead of trusting it.
#
# One retry is normally enough: that console is transient (cmd /C exits when the
# batch does), and keystrokes that land in it are harmless -- the URL arrives at
# a prompt, Enter reports an unrecognised command, and the window closes. The
# check also covers the slower failure where the browser reaches the URL before
# the container it is reporting on has finished its work, since a page that
# renders the wrong thing fails done_image just as an unfocused browser does.
#
# Ctrl+A before the paste is belt and braces. Alt+D already selects the bar, but
# if it went astray the paste would append to whatever is sitting there rather
# than replace it. FindFailed on exhaustion keeps the suite's usual failure
# signature, as open_file_in_dialog and save_page_as_html do.
def navigate_browser(window, url, done_image, attempts=3, settle=3, timeout=30):
    for attempt in range(attempts):
        App(window).focus()
        wait(settle)
        type("d", Key.ALT)
        wait(0.5)
        type("a", Key.CTRL)
        paste_text(url)
        type(Key.ENTER)
        if exists(done_image, timeout):
            return True
        Debug.user("navigate_browser: '%s' did not reach '%s' on attempt %d of %d"
                   % (url, done_image, attempt + 1, attempts))
    raise FindFailed("navigate_browser: '%s' never loaded in %d attempts" % (url, attempts))

# Open a Windows Settings page through the Settings search box, and prove it opened.
#
# Settings does not navigate on Enter by itself. Enter activates the highlighted
# row of the search suggestion list, so it does nothing at all when that list has
# not been drawn yet, and paste() returns as soon as the clipboard is written --
# the fixed wait that used to follow it was a bet on how fast Settings renders.
# In App Tests run 34423171312 (mozilla_firefox-nl) the bet lost: step frame 026,
# taken just before the Enter, shows the box holding "Default apps" with no list
# under it, and frame 027 -- three seconds after the Enter -- shows the list
# finally opening with Settings still on its Home page.
#
# Nothing downstream noticed, which is what made it expensive. The test went on
# clicking, the page it wanted was never on screen, and the run died four lines
# later at an image that page was the only thing that could have shown. So check
# that the page actually opened and redo the search if it did not: by the retry
# the list is up, and the Enter lands on it.
#
# The anchor has to be an image that only the wanted page can show, and it has to
# be matched tightly enough that nothing else on screen can satisfy it -- the
# verification is worth nothing if a stray match elsewhere passes for the page.
# See the search-apps.png note in the firefox tests for what that costs when the
# threshold is left at the default.
#
# search_box_image is the empty box's placeholder ("Find a setting"), which stops
# matching once the box has text in it (0.99 empty, 0.58 typed in), so it is
# waited on once up front and never again; the retry clicks the Match it returned
# and clears the box with Ctrl+A instead. Returns the anchor's Match so the caller
# can click it without searching for it a second time.
def open_settings_page(search_box_image, query, anchor, attempts=3, timeout=20):
    type("i", Key.WIN)
    box = wait(search_box_image)
    for attempt in range(attempts):
        click(box)
        wait(0.5)
        type("a", Key.CTRL)
        paste_text(query)
        type(Key.ENTER)
        found = exists(anchor, timeout)
        if found:
            return found
        Debug.user("open_settings_page: '%s' did not open on attempt %d of %d"
                   % (query, attempt + 1, attempts))
    raise FindFailed("open_settings_page: '%s' never opened in %d attempts" % (query, attempts))

# Give a container's console window the keyboard, and check that it took.
#
# StandardTest -> HidePowerShellWindow (Test.ps1) ends with
# Shell.Application.MinimizeAll() and an ESC keystroke, and nothing after that
# hands the container's console window the foreground. Whether it happens to own
# the keyboard when a test starts typing is a race, and on the win11-arm pool the
# nodejs arm64 tests lost it in 13 of the 15 App Tests results between 2026-09-06
# and 09-09: every keystroke went to the taskbar Search box instead, Edge opened
# on a Bing search for the run of concatenated commands, and the console sat at
# its prompt untouched until the test gave up 4 minutes later. Waiting for an
# image on the window cannot catch this - the console is visible the whole time,
# it just is not focused - which is why the wait("node-cmd-prompt.png") those
# tests already did passed and then typed into nothing.
#
# App(title).focus() is no help here either: a container console's title changes
# while the test runs (cmd.exe -> node-gyp -> cmd.exe for nodejs), and App() name
# matching on container consoles is already unreliable under xvm 26.9.x - a lone
# App("conhost").focus() restored nothing in the ggerganov_llama-cpp runs above.
# So click the window instead, located by an image the caller supplies, and then
# ask which window is actually in front before trusting it.
#
# Returns the Match that was clicked so the caller can go on using it as an
# anchor. Raises FindFailed only if the image never appears: once the window is
# on screen the click is the fix, and the confirmation is a diagnostic that must
# not itself be the reason a test fails.
def focus_console(image, attempts=10, poll=3):
    match = None
    for attempt in range(attempts):
        match = exists(image, poll)
        if match is None:
            continue
        click(match.getTarget())
        # A click in a console with QuickEdit mode on (the Windows 11 default)
        # leaves a zero-width selection anchor; ESC drops it so that it cannot
        # later grow into a selection, which would suspend the console's output.
        type(Key.ESC)
        # Let the activation land before asking what is in front, or the common
        # case - the first click works - still reads the old foreground window
        # and clicks again.
        wait(1)
        if _foreground_covers(match):
            return match
        Debug.user("focus_console: %s is on screen but another window is in front (attempt %d of %d)"
                   % (image, attempt + 1, attempts))
    if match is None:
        raise FindFailed("focus_console: %s never appeared" % image)
    Debug.user("focus_console: could not confirm focus on %s; typing anyway" % image)
    return match

# True when the foreground window's rectangle covers `region`.
#
# This only decides whether focus_console clicks again, so "cannot tell" counts
# as good enough: a SikuliX build that will not report the focused window must
# not turn into a test failure.
def _foreground_covers(region):
    try:
        win = App.focusedWindow()
    except:
        Debug.user("focus_console: cannot read the foreground window: %s" % sys.exc_info()[1])
        return True
    if win is None:
        return False
    return (win.getX() <= region.getX()
            and win.getY() <= region.getY()
            and win.getX() + win.getW() >= region.getX() + region.getW()
            and win.getY() + win.getH() >= region.getY() + region.getH())
