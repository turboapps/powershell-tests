script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("goto_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "GoTo.lnk"))
wait("goto_window.png")

# Check "help".
click(Pattern("menu.png").targetOffset(108,0))
wait(2)
click(Pattern("menu_help.png").targetOffset(-19,49))
wait("about.png")
type(Key.ESC) # For the "about" window.

# There is an issue that when the app is not fully closed (taskbar tray is on),
# URL handler will not work. It is a native behavior.
click(Pattern("menu.png").targetOffset(-113,0))
wait(2)
click("menu_file.png")
wait(5)

# URL handler.
run('explorer "https://global.gotomeeting.com/join/750803053"')
click(Pattern("url_handler.png").targetOffset(138,47))
closeApp("Edge")
wait("join_meeting.png")
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()