script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(70)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
if exists("grafx-warning.png"):
    click(Pattern("grafx-warning.png").targetOffset(255,11))
wait("adobe_login.png")
click(Pattern("adobe_login.png").targetOffset(60,64))
if exists("grafx-warning.png"):
    click(Pattern("grafx-warning.png").targetOffset(255,11))
wait(10)

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Photoshop"))
if exists("grafx-warning.png"):
    click(Pattern("grafx-warning.png").targetOffset(-298,9))
    click(Pattern("grafx-warning.png").targetOffset(255,11))
util.adobe_cc_login(username, password)
wait("photoshop-menu-bar.png")

# Basic operations.
setAutoWaitTimeout(20)
if exists("grafx-warning.png"):
    click(Pattern("grafx-warning.png").targetOffset(-298,9))
    click(Pattern("grafx-warning.png").targetOffset(255,11))
type("o", Key.CTRL)
if exists("on-your-computer.png"):
    click("on-your-computer.png")
wait("file_location.png")
type(os.path.join(script_path, os.pardir, "resources", "sample.png") + Key.ENTER)
wait(5)
type("w", Key.ALT + Key.CTRL + Key.SHIFT)
wait("export-button.png")
click("export-format-drop.png")
click(Pattern("format-select.png").targetOffset(-46,53))
wait(5)
click(Pattern("export-button.png").targetOffset(1,2))
wait(5)
type(os.path.join(util.desktop, "export.gif") + Key.ENTER)
wait(10)
assert(util.file_exists(os.path.join(util.desktop, "export.gif"), 5))
if exists("try-later-button.png"):
    click("try-later-button.png")
type("q",Key.CTRL)
wait(30)

# Check if the session terminates.
util.check_running()