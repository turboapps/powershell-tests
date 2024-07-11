script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(60)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait("adobe-login.png")
click(Pattern("adobe-login.png").targetOffset(62,100))
wait(10)

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Adobe Character Animator 2024.lnk"))
util.adobe_cc_login(username, password)
wait("title-bar.png")

# Basic operations.
setAutoWaitTimeout(20)
wait("lacy_puppet.png")
click(Pattern("lacy_puppet.png").targetOffset(-3,-3))
wait(10)
click(Pattern("quick-export-button.png").targetOffset(1,1))
wait("export.png")
click("export.png")
wait(10)
assert(util.file_exists(os.path.join(os.environ['USERPROFILE'], "Documents\\Adobe\\Character Animator\\Scene - Lacy Starter.mp4"), 5))
type("q",Key.CTRL)

# Check if the session terminates.
wait(10)
util.check_running()