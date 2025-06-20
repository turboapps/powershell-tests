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

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test of `turbo run`.
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
type('turbo run mediaencoder --using=creativeclouddesktop,isolate-edge-wc --offline --enable=disablefontpreload --name=test')
type(Key.ENTER)

# Minimize the command prompt
App().focus("Command Prompt")
type(Key.DOWN, Key.WIN)

if exists("GPUSniffer_error.png",60):
    click(Pattern("GPUSniffer_error_close.png").targetOffset(-49,4))
wait("me_window.png",15)
type("q", Key.CTRL)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Media Encoder"))
if exists("GPUSniffer_error.png",60):
    click(Pattern("GPUSniffer_error_close.png").targetOffset(-49,4))

# Basic operations.
wait("me_window.png",15)
wait(3)
click("me_window.png") # To gain focus.
type("i", Key.CTRL)
wait("source_location.png",10)
type(os.path.join(script_path, os.pardir, "resources", "create-project-import-media", "create-project-import-media-step1.prproj") + Key.ENTER)
wait("loaded.png",10)
type(Key.ENTER)
wait("done.png",10)
wait(10)
assert(util.file_exists(os.path.join(script_path, os.pardir, "resources", "create-project-import-media", "Master Sequence.mp4"), 5))

# Check "help".
type(Key.F1)
wait("help_url.png")
closeApp("Edge")
wait(10)
type("q", Key.CTRL)
wait(10)

# Check if the session terminates.
util.check_running()