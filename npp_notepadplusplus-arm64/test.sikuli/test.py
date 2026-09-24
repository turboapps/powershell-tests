# The tests for npp/notepadplusplus, npp/notepadplusplus-x64 and npp/notepadplusplus-arm64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("npp_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Notepad++.lnk"))
wait("npp_window.png")

# Basic operations.
type("Hello world!")
type("s", Key.CTRL)
wait("save_location.png")
type("%USERPROFILE%\\Desktop\\new 1" + Key.ENTER)
type(Key.F4, Key.ALT)
run("explorer " + util.desktop)
wait(3)
# Select the saved file via Explorer type-ahead and open its context menu with Shift+F10.
# Matching the file entry by screenshot (txt.png at 0.90 similarity) is brittle across
# Windows builds - Explorer renders the entry differently on the win11-arm pool - and
# lowering similarity risks matching the test's own log files on the same Desktop.
type("new 1")
wait(1)
type(Key.F10, Key.SHIFT)
click("shell_edit_with.png")
wait("npp_window.png")
type("p", Key.CTRL)
wait("print_window.png")
type(Key.ESC)

# Check "help".
click("menu.png")
click("menu_help.png")
wait("npp_help_url.png")
# Close the foreground Edge window with Alt+F4. closeApp("Edge") intermittently fails on
# the win11-arm pool on Edge's first-ever (cold) start (see aspnet-runtime tests).
#
# Each window is closed and then confirmed gone before the next keystroke. Three
# back-to-back Alt+F4s assumed every window closes instantly and hands the foreground
# to the next one; in App Tests run 36031790051 Edge took seconds to go away (it
# crashed on the way out, msedge dump 2.7 s after the first Alt+F4), the other two
# keystrokes landed while it was still tearing down, and Notepad++ stayed open with
# the session Running until check_running gave up at line 53.
util.close_window("npp_help_url.png")
# Notepad++ is what keeps the session alive, so wait for its process rather than its
# window, and give it the foreground first so the keystroke cannot land elsewhere.
# Focus it by its document name (the title is "...\new 1.txt - Notepad++"), which
# works even when another window covers it; "Notepad++" itself is not used because,
# read as a pattern, it also matches a plain "Notepad" window. Then, if it is visible,
# click its document tab (bottom-left of npp_window.png), which selects the tab that
# is already selected.
for attempt in range(3):
    util.activate_app_window("new 1.txt", 5)
    if exists("npp_window.png", 5):
        click(Pattern("npp_window.png").targetOffset(-90, 27))
    type(Key.F4, Key.ALT)
    if util.wait_process_gone("notepad++.exe", max_wait=20) >= 0:
        break
# Close the explorer window - only once it holds the foreground: Alt+F4 on the bare
# desktop opens the Shut Down Windows dialog.
if util.activate_app_window("Desktop", 10):
    type(Key.F4, Key.ALT)
# Check if the session terminates.
util.check_running()