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
if exists("hardware-warning.png"):
    click(Pattern("hardware-warning.png").targetOffset(192,55))
if exists("learn-panel.png"):
    click(Pattern("learn-panel.png").targetOffset(8,-28))
    click("close-panel.png")
util.adobe_cc_login(username, password)
wait("audition-title-bar.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Adobe Audition 2024.lnk"))
if exists("hardware-warning.png"):
    click(Pattern("hardware-warning.png").targetOffset(-171,24))
    click(Pattern("hardware-warning.png").targetOffset(192,55))
if exists("learn-panel.png"):
    click(Pattern("learn-panel.png").targetOffset(8,-28))
    click("close-panel.png")
wait("audition-title-bar.png")

# Basic operations.
setAutoWaitTimeout(20)
type("i",Key.CTRL)
wait(5)
type("%USERPROFILE%\\Desktop\\adobe_audition\\resources\\sample.mp3")
type(Key.ENTER)
wait("sample-open.png")
setAutoWaitTimeout(20)
type("e", Key.CTRL + Key.SHIFT)
wait("export-file.png")
type(Key.ENTER)
if exists("export-warning.png"):
    type(Key.ENTER)
wait(10)
assert(util.file_exists(os.path.join(os.environ['USERPROFILE'], "Documents\\sample_01.mp3"), 5))
type("q",Key.CTRL)

# Check if the session terminates.
wait(30)
util.check_running()