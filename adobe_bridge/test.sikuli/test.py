script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(45)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
if exists("gpu_warning.png"):
    click(Pattern("gpu_warning.png").targetOffset(179,88))
if exists("bridge_new.png"):
    type(Key.ESC)
if not exists("adobe_login.png"):
    wait("bridge_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Bridge"))
if exists("gpu_warning.png"):
    click(Pattern("gpu_warning.png").targetOffset(179,88))
if exists("bridge_new.png"):
    type(Key.ESC)
util.adobe_cc_login(username, password)

# Basic operations.
click(Pattern("bridge_window.png").targetOffset(-119,27))
type(Key.RIGHT)
type("adobe_bridge\\resources" + Key.ENTER) # Bridge cannot take relative paths.
wait(2)
click("red-fox-thumbnail.png")
click("Output-menu.png")
rightClick("fox-content.png")
click("add-to-output-doc.png")
wait("output-doc.png")
click("export-pdf.png")
wait("save-pdf.png")
type("%userprofile%\\desktop\\fox.pdf" + Key.ENTER)
util.close_firewall_alert()
closeApp("Edge")

# Check "help".
type(Key.F1)
if exists("help-signin-button.png"):
    click("help-signin-button.png")
wait("bridge-user-guide.png")
closeApp("Edge")
wait(10) # Wait for the complete close of the firewall alert.
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()