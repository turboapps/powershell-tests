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
type(Key.F4, Key.ALT)
type(Key.F4, Key.ALT)
type(Key.F4, Key.ALT) # Close the explorer window
wait(20)
# Check if the session terminates.
util.check_running()