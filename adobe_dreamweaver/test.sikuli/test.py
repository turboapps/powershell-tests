script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
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
type('turbo run dreamweaver --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test')
type(Key.ENTER)

# Minimize the command prompt
App().focus("Command Prompt")
type(Key.DOWN, Key.WIN)

if exists("introducing.png",90):
    click("introducing.png")
    type(Key.ESC)
click(Pattern("sync_settings.png").targetOffset(-12,59))
wait("dw_window.png",20)
type("q", Key.CTRL)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Dreamweaver"))

# Basic operations.
if exists("introducing.png",90):
    click("introducing.png")
    type(Key.ESC)
click(Pattern("sync_settings.png").targetOffset(-12,59)) # To gain the focus.
click(Pattern("sync_settings.png").targetOffset(-12,59))
wait("dw_window.png",20)
type("n", Key.CTRL)
click(Pattern("new.png").targetOffset(0,4))
wait("new_template.png",20)
type(Key.ENTER)
wait("code.png",60)
click("code.png")
type("s", Key.CTRL)
wait("save_location.png",20)
type(save_path + Key.ENTER)
wait(10)
type("w", Key.CTRL + Key.SHIFT)
type("o", Key.CTRL)
wait("open_location.png",20)
type(save_path + Key.ENTER)
wait("code.png",20)

# Check "help".
type(Key.F1)
if exists("help-sign-in.png",30):
    click("help-sign-in.png")
wait("help_url.png",15)
closeApp("Edge")
wait(10)
type("q", Key.CTRL)
wait(10)

# Check if the session terminates.
util.check_running()