script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Test of `turbo run`.
if exists("survey.png"):
    click(Pattern("survey.png").targetOffset(42,0))
wait("fiddler_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Fiddler Classic.lnk"))
if exists("survey.png"):
    click(Pattern("survey.png").targetOffset(42,0))
wait("fiddler_window.png")
run("explorer https://turbo.net")
wait("turbo-net-webpage.png")
wait(5)
closeApp("Edge")
# Basic operations.
wait("turbo-net.png")
doubleClick("turbo-net.png")
click("headers.png")
click("headers.png")
wait("connection-est.png")
closeApp("Edge")

# Check "help".
type(Key.F1)
wait("help_url.png")
closeApp("Edge")
wait(5)
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()