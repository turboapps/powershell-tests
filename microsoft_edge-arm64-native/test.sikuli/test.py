script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)
import subprocess

setAutoWaitTimeout(30)
util.pre_test()

save_location = os.path.join(util.desktop, "print.pdf")

# google.com serves two homepages at random: the classic one with a "Google
# Search" button (webpage.png) and a newer one with "Create images / Ask about
# files / Brainstorm" chips and no such button. The header strip (Gmail,
# Images, apps, Sign in) is on both. 0.85 because Edge's own new-tab page,
# which has a Sign in button too, scores 0.70 against it.
google_anchors = [Pattern("google_header.png").similar(0.85), Pattern("webpage.png").similar(0.60)]

# Edge is installed natively; the executor launched it in a base container named
# "test" and recorded the command line in launch.txt (NativeTest.ps1 Start-NativeApp).
# Every relaunch goes through the same container, never a Start menu shortcut or a
# file association, which would start the native Edge outside it.
def launch(*args):
    with open(os.path.join(script_path, os.pardir, "launch.txt")) as f:
        command, app_args = (f.read().splitlines() + ["", ""])[:2]
    subprocess.Popen(command + " -d -- " + " ".join([app_args] + ['"%s"' % a for a in args]))

def wait_google(timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        for anchor in google_anchors:
            match = exists(anchor, 0)
            if match:
                return match
        wait(1)
    return wait(google_anchors[0], 0)  # FindFailed names the header anchor

# Test of `turbo run`.
wait("new-tab.png")
run("turbo stop test")
wait(10)

# Launch the app.
util.wait_app_quiet("msedge.exe")
launch()
wait("new-tab.png")
click("new-tab.png")

# Activate and maximize the app window.
app_window = App().focus("Edge")
if app_window.isValid():
    type(Key.UP, Key.WIN)

# Basic operations.
click(Pattern("address-bar.png").targetOffset(16,1))
if exists("about-blank.png",5):
    click("about-blank.png")
type("https://google.com/" + Key.ENTER)
wait_google()
wait(3)
type("s", Key.CTRL)
wait("save_type.png")
type(os.path.join(util.desktop, "name with space"))
click("save_type.png")
click("save_type_correct.png")
type(Key.ENTER)
wait(20)
type(Key.ESC)
assert util.file_exists(os.path.join(util.desktop, "name with space.html"), 6)
if App("Edge").isRunning(10):
    util.close_app("Edge")

# Open the saved page and a URL by handing them to Edge in the container. (The
# image-based test opens them through Windows' default browser instead, which here
# would be the native Edge outside the container.)
util.wait_app_quiet("msedge.exe")
launch(os.path.join(util.desktop, "name with space.html"))
wait_google()
if App("Edge").isRunning(10):
    util.close_app("Edge")
util.wait_app_quiet("msedge.exe")
launch("https://google.com/")
# To gain focus: blank page below the anchor, never the header links.
click(wait_google().getTarget().offset(0, 200))
wait(5)
type("p", Key.CTRL)
wait("print_window.png")
click(Pattern("print_print.png").targetOffset(-64,1))
wait("print_location.png")
wait(2)
paste(save_location)
wait(2)
type(Key.ENTER)
assert(util.file_exists(save_location, 5))

click("menu.png")
click(Pattern("menu_content.png").targetOffset(0,-14))
wait("setting_page.png")
wait(10)

# Check "help".
type(Key.F1)
wait("help_url.png")
if App("Edge").isRunning(10):
    util.close_app("Edge")
wait(20)

# Check if the session terminates.
util.check_running()

# The Edge DLLs (Edge, Edge Beta, EdgeWebView) must load from the native install, not
# be faulted into the container's sandbox.
util.assert_no_faulted_dlls([r"@PROGRAMFILESX86@\Microsoft\Edge", r"@PROGRAMFILES@\Microsoft\Edge"])
