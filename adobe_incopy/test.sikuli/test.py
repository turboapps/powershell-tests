script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import subprocess
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(45)
save_path = os.path.join(util.desktop, "test.icml")

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test of `turbo run`.
subprocess.Popen("turbo run incopy --using=creativeclouddesktop,isolate-edge-wc --offline --enable=disablefontpreload --network=test --name=test")
wait(3)
type(Key.ENTER)
if exists("adobe_login_signout_others.png",120):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("adobe_login_team.png",10):
    click(Pattern("adobe_login_continue.png").similar(0.80))
wait("incopy_window.png",20)
run("turbo stop test")
closeApp("Command Prompt")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe InCopy"))

# Basic operations.
wait("incopy_window.png",120)
wait(10)
click("incopy_window.png")
type("n", Key.CTRL)
wait("new_document.png")
type(Key.ENTER)
wait("new_file.png")
paste("test")
click(Pattern("new_file.png").targetOffset(61,12))
wait("layout_view.png")
type("s", Key.CTRL + Key.SHIFT)
wait("save_location.png")
paste(save_path)
type(Key.ENTER)
wait("user.png")
paste(save_path) 
type(Key.ENTER)
assert(util.file_exists(save_path, 5))
type("q", Key.CTRL)
wait(30)
run("explorer " + save_path)
wait("untitled-1.png",120)

# Check "help".
# Launch help twice as it sometimes fails the first time
type(Key.F1)
wait(10)
closeApp("Edge")
type(Key.F1)
wait("help_url.png",30)
closeApp("Edge")
wait(10)
type("q", Key.CTRL)
wait(10)

# Check if the session terminates.
util.check_running()