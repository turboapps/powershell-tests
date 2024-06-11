script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

save_path = os.path.join(util.desktop, "red fox.jpg")

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("pdn_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "paint.net.lnk"))
wait("pdn_window.png")

# Basic operations.
type("o", Key.CTRL)
click("open_location.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("loaded.png")
type("g", Key.CTRL + Key.SHIFT)
wait("processed.png")
wait(5)
type("s", Key.CTRL + Key.SHIFT)
wait("save_location.png")
type(save_path + Key.ENTER)
click(Pattern("save_ok.png").targetOffset(-40,5))

# Check "help".
type(Key.F1)
util.close_firewall_alert()
wait("help_url.png")
closeApp("Edge")
wait(10) # Wait for the complete close of the firewall alert
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()

# Export might be slow.
assert(os.path.exists(save_path))