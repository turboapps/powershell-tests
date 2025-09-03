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
type('turbo run premierepro --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test')
type(Key.ENTER)

# minimize the command prompt
cmd_prompt = App().focus("Command Prompt")
if cmd_prompt.isValid():
    type(Key.DOWN, Key.WIN)
    
wait("pr_window.png", 180)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Premiere Pro"))

# Basic operations.
wait("pr_window.png", 180)
click("pr_window.png") # To gain focus.
type("o", Key.CTRL)
wait("location.png")
type(os.path.join(script_path, os.pardir, "resources", "create-project-import-media", "create-project-import-media-step1.prproj") + Key.ENTER)
wait("convert_prompt.png")
click("ok-button.png")
if exists("no_output_device.png",30):
    click(Pattern("no_output_device.png").targetOffset(137,53))
if exists("panel_rename.png"):
    click(Pattern("panel_rename_close.png").targetOffset(-2,-10))
wait("timeline.png")

# Check "help".
type(Key.F1)
wait("help_url.png")
closeApp("Edge")
wait(10)
click("timeline.png") # Gain focus.
type(Key.F4, Key.ALT)
if exists("dont-save.png",10):
    click("dont-save.png")
wait(10)

# Check if the session terminates.
util.check_running()