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
wait(60)
wait("adobe_login.png")
run("turbo stop test")

# Launch the app.
wait(30)
run("explorer " + os.path.join(util.start_menu, "Adobe Animate 2024.lnk"))
wait(60)
util.adobe_cc_login(username, password)
wait("animate-launched.png")
if exists("new-to-animate.png"):
    click(Pattern("new-to-animate.png").targetOffset(-50,12))

# Basic operations.
wait("canvas.png")
type("n",Key.CTRL+Key.SHIFT)
wait("html5-canvas.png")
click("html5-canvas.png")
type(Key.ENTER)
type("s",Key.CTRL+Key.ALT+Key.SHIFT)
type("%USERPROFILE%\\Desktop\\Test.gif")
type(Key.TAB)
type("g")
type(Key.ENTER)
type(Key.ENTER)
wait(10)
assert(util.file_exists(os.path.join(os.environ['USERPROFILE'], "Desktop\\test0001.gif"), 5))

# Test video.
click("test-movie-button.png")
util.close_firewall_alert()
wait("movie-url.png")
closeApp("Edge")
type("q",Key.CTRL)

# Check if the session terminates.
wait(10)
util.check_running()