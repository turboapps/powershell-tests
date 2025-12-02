script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(45)

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
paste('turbo run bridge --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test')
wait(2)
type(Key.ENTER)
if exists("adobe_login_signout_others.png",60):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("adobe_login_team.png",10):
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("gpu_warning.png"):
    click(Pattern("gpu_warning.png").targetOffset(179,88))
if exists("bridge_new.png"):
    type(Key.ESC)
wait("bridge_window.png")
run("turbo stop test")
closeApp("Command Prompt")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Bridge"))
if exists("gpu_warning.png",60):
    click(Pattern("gpu_warning.png").targetOffset(179,88))
if exists("bridge_new.png"):
    type(Key.ESC)
wait("bridge_window.png")

# Basic operations.
click(Pattern("bridge_window.png").targetOffset(-119,27))
type(Key.RIGHT)
paste("adobe_bridge\\resources")  # Bridge cannot take relative paths.
wait(2)
type(Key.ENTER)
wait(5)
click("red-fox-thumbnail.png")
click("Output-menu.png")
rightClick("fox-content.png")
click("add-to-output-doc.png")
wait("output-doc.png")
click("export-pdf.png")
wait("save-pdf.png")
wait(10)
paste("%userprofile%\\desktop\\fox.pdf")
wait(2)
type(Key.ENTER)
wait("fox-output.png")
closeApp("Edge")

# Check "help".
type(Key.F1)
if exists("help-sign-in.png",15):
    click("help-sign-in.png")
wait("bridge-user-guide.png")
closeApp("Edge")
wait(10)
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()
