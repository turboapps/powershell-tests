script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(90)

util.pre_test()

# One more time is needed for java window.
App("java.exe").focus()
type(Key.DOWN, Key.WIN)

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
util.adobe_cc_login(username, password)
if exists("cc_discontinued_top.png"):
    click(Pattern("cc_discontinued_top.png").targetOffset(52,-19)) # To gain focus
    click(Pattern("cc_discontinued.png").targetOffset(173,30))
wait("rush_window_1.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Adobe Premiere Rush.lnk"))

# Basic operations.
click(Pattern("rush_window_2.png").targetOffset(0,-59))
if exists("project_setup.png"):
    click(Pattern("project_setup.png").targetOffset(85,53))
if exists("sync.png"):
    click(Pattern("sync.png").targetOffset(-75,-2))
click("add_2.png")
wait("add_resources.png")
type("a", Key.CTRL)
click("add_create.png")
wait("loaded.png")

# Check "help".
type(Key.F1)
util.close_firewall_alert()
wait("help_url.png")
closeApp("Edge")
wait(10)
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()