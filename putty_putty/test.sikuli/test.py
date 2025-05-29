script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
host = credentials.get("host")
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait("putty_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "PuTTY (64-bit)", "PuTTY.lnk"))
wait("putty_window.png")

# Check "help".
click(Pattern("putty_window.png").targetOffset(-88,204))
click("help.png")
type(Key.F4, Key.ALT)

# Basic operations.
click(Pattern("putty_window.png").targetOffset(-53,-100))
type(host + Key.ENTER)
click(Pattern("finger_print.png").targetOffset(113,47))
wait("username.png")
type(username + Key.ENTER)
wait("password.png")
type(password + Key.ENTER)

wait("logged_in.png") # This screenshot is specific to a test environment.
type(Key.F4, Key.ALT)
click(Pattern("close.png").targetOffset(23,38))
click("telnet-exit.png")

# Check if the session terminates.
util.check_running()