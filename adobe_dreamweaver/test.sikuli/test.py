script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(90)
save_path = include_path = os.path.join(util.desktop, "test", "test")

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
if exists("introducing.png"):
    click("introducing.png")
    type(Key.ESC)
util.close_firewall_alert()
util.adobe_cc_login(username, password)
click(Pattern("sync_settings.png").targetOffset(-12,59))
wait("dw_window.png")
type("q", Key.CTRL)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Dreamweaver"))

# Basic operations.
if exists("introducing.png"):
    click("introducing.png")
    type(Key.ESC)
util.close_firewall_alert()
click(Pattern("sync_settings.png").targetOffset(-12,59)) # To gain the focus.
click(Pattern("sync_settings.png").targetOffset(-12,59))
wait("dw_window.png")
type("n", Key.CTRL)
click(Pattern("new.png").targetOffset(0,4))
wait("new_template.png")
type(Key.ENTER)
wait("code.png")
type("s", Key.CTRL)
wait("save_location.png")
type(save_path + Key.ENTER)
wait(10)
type("w", Key.CTRL + Key.SHIFT)
type("o", Key.CTRL)
wait("open_location.png")
type(save_path + Key.ENTER)
wait("code.png")

# Check "help".
type(Key.F1)
wait("help_url.png")
closeApp("Edge")
wait(10)
type("q", Key.CTRL)
wait(10)

# Check if the session terminates.
util.check_running()