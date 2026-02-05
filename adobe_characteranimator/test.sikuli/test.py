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
type('turbo run characteranimator --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test')
type(Key.ENTER)
wait("title-bar.png",60)
if exists("adobe_login_signout_others.png", 20):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
wait("lacy_puppet.png",60)
wait(10)
type("q",Key.CTRL)
wait(5)
closeApp("Command Prompt")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Character Animator"))
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