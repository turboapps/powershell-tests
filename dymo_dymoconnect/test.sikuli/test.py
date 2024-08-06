script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# Test of `turbo run`.
wait("tips.png")
run("turbo stop test")
wait(10)

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "DYMO", "DYMO Connect", "DYMO Connect.lnk"))
click(Pattern("tips.png").targetOffset(178,-75))

# Basic operations.
wait("dymo_window.png")
click("add.png")
wait(2)
click(Pattern("add_menu.png").targetOffset(-21,-36))
doubleClick("textbox.png")
type("Test")
wait("result.png")
type("p", Key.CTRL)
wait("print_window.png")
click("print_cancel.png")

# Check "help".
type(Key.F1)
util.close_firewall_alert()
wait("help_url.png")
closeApp("Edge")
wait(5)
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()