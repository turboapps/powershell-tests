script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(40)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait("agreement.png",120)
wait(5)
click("agreement.png")
type(Key.ENTER)
wait(10)
type(Key.F4, Key.ALT)
wait(5)
type(Key.F4, Key.ALT)
wait(10)

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.desktop, "Bluebeam Revu"))
wait("agreement.png",120)
wait(5)
click("agreement.png")
type(Key.ENTER)
wait("email-box.png")
click("email-box.png")
type(username)
type(Key.ENTER)
wait("password-box.png")
click("password-box.png")
type(password)
type(Key.ENTER)
wait(5)
type(Key.F4, Key.ALT)

# Launch sample pdf.
run("explorer " + os.path.join(script_path, os.pardir, "resources"))
wait(5)
rightClick("sample-pdf-file.png")
click("open-with-menu.png")
click("choose-another-app.png")
wait("open-with.png")
click(Pattern("open-with.png").targetOffset(-25,65))
click("always.png")
wait("confirm-ok.png",120)
click("confirm-ok.png")
wait("gfx-warning.png",10)
click("gfx-warning.png")
wait("pdf-loaded.png")

# Check "help".
type(Key.F1)
wait("help-window.png")
closeApp("Revu")
wait(60)

# Check if the session terminates.
util.check_running()
