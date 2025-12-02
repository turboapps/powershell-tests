script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(90)

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
paste('turbo run aftereffects --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test')
wait(2)
type(Key.ENTER)

# Minimize the command prompt
App().focus("Command Prompt")
type(Key.DOWN, Key.WIN)
if exists("ram-warning.png",180):
    click("ram-warning.png")
if exists("adobe_login_signout_others.png",60):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("adobe_login_team.png",10):
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("warning.png",60):
    click("warning.png")
    wait(2)
    type(Key.ENTER)
wait("new-file-button.png",20)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe After Effects"))
if exists("ram-warning.png",180):
    click("ram-warning.png")
if exists("warning.png",60):
    click("warning.png")
    wait(2)
    type(Key.ENTER)

# Basic operations.
wait("new-file-button.png",20)
type("i",Key.CTRL)
wait(5)
paste(os.path.join(script_path, os.pardir, "resources", "sample.mp4"))
wait(2)
type(Key.ENTER)
wait("sample-mp4.png",20)
doubleClick(Pattern("sample-mp4.png").targetOffset(-6,7))

# Check "Help".
type(Key.F1)
wait("help_url.png",30)
closeApp("Edge")
type("q",Key.CTRL)
click("save_no.png")
wait(10)

# Check if the session terminates.
util.check_running()
