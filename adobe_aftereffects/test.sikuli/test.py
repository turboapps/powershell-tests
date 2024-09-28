script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(75)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
if exists("dont-send.png",45):
    click("dont-send.png")
if not exists("adobe_login.png"):
    wait("warning.png")
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe After Effects"))
if exists("dont-send.png",45):
    click("dont-send.png")
if exists("warning.png",15):
    click("warning.png")
    type(Key.ENTER)
util.adobe_cc_login(username, password)

# Basic operations.
if exists("warning.png",15):
    click("warning.png")
    type(Key.ENTER)
wait("new-file-button.png")
type("i",Key.CTRL)
wait(5)
type(os.path.join(script_path, os.pardir, "resources", "sample.mp4") + Key.ENTER)
wait("sample-mp4.png")
doubleClick(Pattern("sample-mp4.png").targetOffset(-6,7))

# Check "Help".
type(Key.F1)
type("q",Key.CTRL)
click("dont-save-button.png")
wait(10)

# Check if the session terminates.
util.check_running()
