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
if exists("GPUSniffer_error.png"):
    click(Pattern("GPUSniffer_error_close.png").targetOffset(-49,4))
util.adobe_cc_login(username, password)
wait("me_window.png")
type("q", Key.CTRL)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Media Encoder"))
if exists("GPUSniffer_error.png"):
    click(Pattern("GPUSniffer_error_close.png").targetOffset(-49,4))

# Basic operations.
wait("me_window.png")
type("i", Key.CTRL)
wait("source_location.png")
type(os.path.join(script_path, os.pardir, "resources", "create-project-import-media", "create-project-import-media-step1.prproj") + Key.ENTER)
wait("loaded.png")
type(Key.ENTER)
wait("done.png")
wait(10)
assert(util.file_exists(os.path.join(script_path, os.pardir, "resources", "create-project-import-media", "Master Sequence.mp4"), 5))

# Check "help".
type(Key.F1)
util.close_firewall_alert()
if exists("confirm_account.png"):
    click(Pattern("confirm_account.png").targetOffset(165,139))
wait("help_url.png")
closeApp("Edge")
wait(10)
type("q", Key.CTRL)
wait(10)

# Check if the session terminates.
util.check_running()