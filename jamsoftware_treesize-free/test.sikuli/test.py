# The tests for google/chrome and google/chrome-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("select-directory.png")
type(Key.F4, Key.ALT)
wait(5)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(os.path.join(util.start_menu, "TreeSize Free"), "TreeSize Free"))
wait("select-directory.png")
type("f", Key.ALT)
wait(3)
type("d")
wait(3)
type(include_path + Key.ENTER)
wait("location.png")
click("select-folder-button.png")
wait("100-percent.png")
# check that updates are disabled
click("help-menu.png")
wait("disabled-update-button.png")
click("show-help.png")
wait("help-window.png")
# Close Help
type(Key.F4, Key.ALT)
wait(3)
# Close app
type(Key.F4, Key.ALT)

# Test shell context menu
run("explorer c:\\")
rightClick("sikuli-folder.png")
click("context-menu.png")
# Activate and maximize the app window.
app_window = App().focus("TreeSize Free")
if app_window.isValid():
    type(Key.UP, Key.WIN)

wait("100-percent.png")

type(Key.F4, Key.ALT)
wait(5)

# Check if the session terminates.
util.check_running()