script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(90)
save_path = include_path = os.path.join(util.desktop, "test.indd")

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait(180) # It's a bug that InDesign Launch is super slow.
util.adobe_cc_login(username, password, False)
wait("indesign_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe InDesign"))
wait(180) # It's a bug that InDesign Launch is super slow.

# Basic operations.
wait("indesign_window.png")
type("n", Key.CTRL)
wait("new_project.png")
type(Key.ENTER)
wait("welcome.png")
type(Key.ESC)
wait("new_file.png")
type("s", Key.CTRL)
wait("save_location.png")
type(save_path + Key.ENTER)
assert(util.file_exists(save_path, 5))
run("explorer " + os.path.join(script_path, os.pardir, "resources", "Save.indd"))
click(Pattern("missing_fonts.png").targetOffset(205,155))
wait("open-doc.png")

# Check "help".
type(Key.F1)
util.close_firewall_alert()
App("Edge").focus()
wait("help_url.png")
closeApp("Edge")
wait(10)
type(Key.F4, Key.ALT)
click(Pattern("save.png").targetOffset(101,25))
wait(10)

# Check if the session terminates.
util.check_running()