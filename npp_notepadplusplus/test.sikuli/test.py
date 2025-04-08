# The tests for npp/notepadplusplus and npp/notepadplusplus-x64 are the same.

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
rightClick(Pattern("txt.png").similar(0.90))
click("shell_edit_with.png")
wait("npp_window.png")
type("p", Key.CTRL)
wait("print_window.png")
type(Key.ESC)

# Check "help".
click("menu.png")
click("menu_help.png")
wait("npp_help_url.png")
closeApp("Edge")
type(Key.F4, Key.ALT)
type(Key.F4, Key.ALT) # Close the explorer window
wait(20)
# Check if the session terminates.
util.check_running()