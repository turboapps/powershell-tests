script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(90)
save_path = include_path = os.path.join(util.desktop, "test.indd")

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
paste('turbo run indesign --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test')
type(Key.ENTER)
wait("indesign_window.png",300)
run("turbo stop test")
wait(20)
closeApp("Command Prompt")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe InDesign"))

# Basic operations.
wait("indesign_window.png",300)
if exists("close-blue-banner.png",20):
    click("close-blue-banner.png")
type("n", Key.CTRL)
wait("new_project.png")
type(Key.ENTER)
if exists("welcome.png", 15):
    type(Key.ESC)
wait("new_file.png")
wait(15)
type("s", Key.CTRL)
click("save_cc.png")
wait("save_location.png")
paste(save_path)
type(Key.ENTER)
assert(util.file_exists(save_path, 5))
run("explorer " + os.path.join(script_path, os.pardir, "resources", "Save.indd"))
wait("missing_fonts.png",120)
click(Pattern("missing_fonts.png").targetOffset(205,155))
wait("open-doc.png")

# Check "help".
type(Key.F1)
wait("help_url.png")
closeApp("Edge")
wait(10)
type(Key.F4, Key.ALT)
click(Pattern("save.png").targetOffset(101,25))
wait(10)

# Check if the session terminates.
util.check_running()