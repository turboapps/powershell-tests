script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(90)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
if exists("GPUSniffer_error.png"):
    click(Pattern("GPUSniffer_error_close.png").targetOffset(-49,4))
util.adobe_cc_login(username, password)
wait("pr_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Premiere Pro"))
if exists("GPUSniffer_error.png"):
    click(Pattern("GPUSniffer_error_close.png").targetOffset(-49,4))

# Basic operations.
wait("pr_window.png")
type("o", Key.CTRL)
wait("location.png")
type(os.path.join(script_path, os.pardir, "resources", "create-project-import-media", "create-project-import-media-step1.prproj") + Key.ENTER)
click(Pattern("convert_prompt.png").targetOffset(192,15))
if exists("no_output_device.png"):
    click(Pattern("no_output_device.png").targetOffset(135,55))
if exists("renamed.png"):
    click(Pattern("renamed.png").targetOffset(274,-25))
wait("timeline.png")

# Check "help".
type(Key.F1)
util.close_firewall_alert()
App("Edge").focus() # Edge will lose focus after closing the firewall alert.
wait("help_url.png")
closeApp("Edge")
wait(10)
if exists("renamed.png"):
    click(Pattern("renamed.png").targetOffset(274,-25))
click("timeline.png") # Gain focus.
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()