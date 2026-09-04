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
    wait(Pattern("adobe_login_pass.png").similar(0.40),15)
    wait(3)
    click(Pattern("adobe_login_pass.png").similar(0.40))
    wait(3)
    paste(password)
    wait(3)
    type(Key.ENTER)
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

# Check if the most recently created Turbo session is terminated.
# It is usually the session for the app to be tested.
def check_running(max_retries=12, delay=5):
    for attempt in range(max_retries):
        output = run("turbo sessions -l")
        if "Running" not in output:
            # The session has ended: its VM logs are complete and about to be
            # wiped if the test launches the app again, so copy them out now.
            collect_vm_logs()
            return
        time.sleep(delay)
    assert "Running" not in output

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
