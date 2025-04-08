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

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test turbo run
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
type('turbo run animate --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test')
type(Key.ENTER)
wait("animate-launched.png",120)
run("turbo stop test")
closeApp("Command Prompt")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Adobe Animate 2024.lnk"))
wait("animate-launched.png",120)
if exists("new-to-animate.png"):
    click(Pattern("new-to-animate.png").targetOffset(-50,12))

# Basic operations.
wait("canvas.png")
wait("home.png")
wait(5)
click("home.png")
wait(5)
type("n",Key.CTRL+Key.SHIFT)
wait("html5-canvas.png")
click("html5-canvas.png")
type(Key.ENTER)
wait(10)
type("s",Key.CTRL+Key.ALT+Key.SHIFT)
wait("save_location.png")
wait(5)
type("%USERPROFILE%\\Desktop\\Test.gif")
type(Key.TAB)
wait(3)
type("g")
type(Key.ENTER)
type(Key.ENTER)
wait(10)
assert(util.file_exists(os.path.join(os.environ['USERPROFILE'], "Desktop\\test0001.gif"), 5))

# Test video.
click("test-movie-button.png")
wait("movie-url.png")
closeApp("Edge")
type("q",Key.CTRL)

# Check if the session terminates.
wait(10)
util.check_running()