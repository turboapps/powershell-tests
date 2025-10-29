script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(70)

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
paste('turbo run photoshop --using=creativeclouddesktop,isolate-edge-wc --isolate=merge-user --offline --enable=disablefontpreload --name=test')
type(Key.ENTER)

# Minimize the command prompt
App().focus("Command Prompt")
type(Key.DOWN, Key.WIN)

if exists("grafx-warning.png",90):
    click(Pattern("grafx-warning.png").targetOffset(255,11))
run("turbo stop test")
wait(20)

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Photoshop"))
if exists("grafx-warning.png",90):
    click(Pattern("grafx-warning.png").targetOffset(-298,9))
    click(Pattern("grafx-warning.png").targetOffset(255,11))
wait("photoshop-menu-bar.png",15)

# Basic operations.
setAutoWaitTimeout(20)
type("o", Key.CTRL)
if exists("on-your-computer.png",15):
    click("on-your-computer.png")
wait("file_location.png",10)
paste(os.path.join(script_path, os.pardir, "resources", "sample.png"))
type(Key.ENTER)
wait(5)
type("w", Key.ALT + Key.CTRL + Key.SHIFT)
wait("export-button.png",15)
click("export-format-drop.png")
click(Pattern("format-select.png").targetOffset(-46,53))
wait(5)
click(Pattern("export-button.png").targetOffset(1,2))
wait(5)
paste(os.path.join(util.desktop, "export.gif"))
type(Key.ENTER)
wait(10)
assert(util.file_exists(os.path.join(util.desktop, "export.gif"), 5))
if exists("try-later-button.png",10):
    click("try-later-button.png")
type("q",Key.CTRL)
wait(30)

# Check if the session terminates.
util.check_running()