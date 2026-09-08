# The tests for google/chrome and google/chrome-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import time
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# The TreeSize main window, whether or not the first-run splash is over it: the
# "Select scan target" ribbon button sits above the splash, and it is the only
# reference here that is unique to the app. program-files.png cannot stand in
# for it - that one is TreeSize's address bar, and it scores 0.69 against
# Explorer's own "Program Files" row, too close to SikuliX's 0.7 threshold to
# tell the two windows apart.
TREESIZE_WINDOW = "select-scan-target.png"

# Click TreeSize's "Easily Getting Started!" trial splash away if it is up, and
# say whether it was.
#
# The splash is modal over the main window and does not answer Alt+F4 itself, so
# every wait and every close has to be able to clear it. It also comes up more
# than once: in App Tests runs 34269861733 and 34269865181 a second splash
# arrived moments after the first had been dismissed, with the scan already
# under way.
def dismiss_trial_splash(timeout=2):
    if exists("continue-with-trial.png", timeout):
        click("continue-with-trial.png")
        return True
    return False

# Wait for a shell context menu launch to reach its scan of (target_image),
# dismissing the "Easily Getting Started!" trial splash on the way.
#
# The splash and the main window come up together, about half a minute after the
# launch on a cold container - which is exactly the ambient
# setAutoWaitTimeout(30) that a bare `if exists("continue-with-trial.png")`
# inherits. In App Tests run 34097555049 that exists() lost the race by a second
# or two, returned False, and the splash then appeared and covered the address
# bar, so the wait for the scan target failed 30 s later against an image the
# splash was sitting on top of. Poll the two together instead: the splash covers
# the address bar, so the target being readable is itself proof the splash is
# gone, whichever order the two windows arrive in.
def wait_for_scan(target_image, timeout=180):
    wait(TREESIZE_WINDOW, timeout)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if exists(target_image, 5):
            return
        dismiss_trial_splash()
    raise FindFailed("%s: TreeSize did not scan it within %d s" % (target_image, timeout))

# Close a TreeSize window and confirm it is gone before the test moves on.
#
# Alt+F4 sent to TreeSize while a scan is still running is not acted on until
# the scan finishes, and the reference the test waits for before closing -
# TreeSize's address bar - fills in when the scan STARTS, so the old
# wait("program-files.png") + wait(3) closed the window mid-scan. In App Tests
# run 34097578991 it was still up four seconds later and the right-click that
# followed found sikuli-folder.png in TreeSize's own title bar,
# "C:\Program Files\ - TreeSize (Administrator)" - the same text in the same
# font on the same white as the Explorer row the reference was cropped from,
# matching at 0.834 - so no shell context menu opened and the test died at the
# next image, three lines from the actual fault.
#
# So send Alt+F4 once and then wait the window out, clearing the splash if one
# turns up. A splash that arrives after the scan target became readable is what
# broke App Tests run 34269857819: the close went into the splash, which
# swallowed it, and the window then sat there for three minutes with the app
# responding normally behind it. Clearing a splash therefore means the keystroke
# was lost and has to be sent again - and that is the ONLY thing that re-sends
# it, because a splash on screen is itself proof TreeSize is still up.
#
# Re-sending on a timer instead is what broke run 34271577102: the second Alt+F4
# went out six seconds after the first, into the gap while TreeSize was still
# tearing down (the step frames put the anchor at 0.96 when it was checked and
# 0.34 two seconds later, when the keystroke went out), so Explorer took the
# foreground and closed instead, and the right-clicks that followed had no window
# to aim at.
#
# Polled with exists() rather than waitVanish() so each look leaves a step frame
# and a window that will not close is visible in the diagnostics.
def close_window(anchor, timeout=180, poll=5):
    deadline = time.time() + timeout
    type(Key.F4, Key.ALT)
    while True:
        if dismiss_trial_splash(1):
            wait(1)
            type(Key.F4, Key.ALT)
        if not exists(anchor, 1):
            return
        if time.time() >= deadline:
            break
        wait(poll)
    Debug.user("close_window: %s still on screen %d s after Alt+F4" % (anchor, timeout))
    raise FindFailed("%s: the window did not close" % anchor)

# Test of `turbo run`.
wait("license-prompt.png")
type(Key.F4, Key.ALT)
wait(5)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(os.path.join(util.start_menu, "TreeSize"), "TreeSize"))
wait("license-prompt.png")
click("license-ok.png")
wait(TREESIZE_WINDOW)
type("f", Key.ALT)
type("t")
click("directory.png")
click("desktop.png")
click("confirm-selection.png")
wait("edge-lnk.png")
wait(5)
# Close app
close_window(TREESIZE_WINDOW)

# Test shell context menu
run("explorer c:\\")
wait("sikuli-folder.png")
wait(2)
# Pin the folder row rather than re-finding it before every right-click: the
# first right-click selects the row, and the highlighted row no longer matches
# the reference (0.55) while the unselected "Program Files (x86)" row below it
# matches better (0.90), so a re-search silently walks down the list.
folder = find("sikuli-folder.png")

rightClick(folder)
click("treesize-context-menu.png")
wait_for_scan("program-files.png")
close_window(TREESIZE_WINDOW)

rightClick(folder)
click("adv-file-search.png")
wait("search-configuration.png")
wait(10)
close_window("search-configuration.png")

rightClick(folder)
click("find-files-context.png")
wait("basic-search.png")
wait(10)
close_window("basic-search.png")
wait(5)

# Check if the session terminates.
util.check_running()
