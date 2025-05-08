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
type('turbo run audition --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test')
type(Key.ENTER)
if exists("learn-panel.png",60):
    click(Pattern("learn-panel.png").targetOffset(8,-28))
    click("close-panel.png")
wait(5)
type("q",Key.CTRL)
wait(5)
closeApp("Command Prompt")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Audition"))
if exists("hardware-warning.png"):
    click(Pattern("hardware-warning.png").targetOffset(-173,7))
    click(Pattern("hardware-warning.png").targetOffset(192,38))
if exists("learn-panel.png",60):
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