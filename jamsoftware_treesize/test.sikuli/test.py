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
        if exists("continue-with-trial.png", 2):
            click("continue-with-trial.png")
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
# Wait the window out instead of guessing at a settle, and re-send Alt+F4 only
# after re-focusing the app, so a stray keystroke can never close Explorer out
# from under the right-clicks that follow.
def close_window(anchor, settle=90, attempts=2):
    for attempt in range(attempts):
        type(Key.F4, Key.ALT)
        if wait_gone(anchor, settle):
            return
        Debug.user("close_window: %s still on screen %d s after Alt+F4 (attempt %d of %d)"
                   % (anchor, settle, attempt + 1, attempts))
        if not util.activate_app_window("TreeSize", 10):
            break
    raise FindFailed("%s: the window did not close" % anchor)

# True once (anchor) is off the screen, False if it is still there at (timeout).
# Polled with exists() rather than waitVanish() so each look leaves a step frame
# and a window that never closes is visible in the diagnostics; the sleep
# between looks keeps a still-open window from spinning the loop, since exists()
# returns the moment it finds its image.
def wait_gone(anchor, timeout, poll=5):
    deadline = time.time() + timeout
    while True:
        if not exists(anchor, 1):
            return True
        if time.time() >= deadline:
            return False
        wait(poll)

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
