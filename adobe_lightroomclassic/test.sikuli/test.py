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

# Test of `turbo run`.
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
type('turbo run lightroomclassic --using=creativeclouddesktop,isolate-edge-wc --offline --enable=disablefontpreload --name=test')
type(Key.ENTER)

# Minimize the command prompt
App().focus("Command Prompt")
type(Key.DOWN, Key.WIN)

if exists("whats_new_close.png",90):
    click("whats_new_close.png")
if exists("getting_started.png",15):
    click(Pattern("getting_started.png").targetOffset(186,-18))
wait(15)
run("turbo stop test")
wait(10)

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Adobe Lightroom Classic.lnk"))
if exists("whats_new_close.png",90):
    click("whats_new_close.png")
if exists("getting_started.png",15):
    click(Pattern("getting_started.png").targetOffset(186,-18))

# Basic operations.
wait("lightroomcc_window.png",30)
type("i", Key.CTRL + Key.SHIFT)
click("import_select_source.png")
click("import_select_source_menu.png")
wait("import_location.png",20)
type(os.path.join(script_path, os.pardir, "resources") + Key.ENTER)
wait(2)
type(Key.ENTER)
wait("import_thumbnail.png",10)
click("import_import.png")
wait("import_done.png",20)
type("d")
wait(2) # Wait for Edit panel to load.
if exists("develop_mode.png",30):
    click(Pattern("develop_mode.png").targetOffset(181,-96))
if exists("point_color.png",15):
    click(Pattern("point_color.png").targetOffset(219,-54))
type("r")
wait(2)
type("x")
wait(2)
type(Key.ENTER)
wait("adjusted.png",15)
type("e", Key.CTRL + Key.SHIFT)
wait("export.png",15)
type(Key.ENTER)

# Check "help".
type(Key.F1)
wait("help_url.png",30)
closeApp("Edge")
wait(10)
if exists("import_select_source.png",10):
    wait(2)
    click("import_cancel.png")
type("q", Key.CTRL)
click(Pattern("quit.png").targetOffset(101,28))
wait(30)

# Check if the session terminates.
util.check_running()

# Export might be slow.
assert(util.file_exists(os.path.join(util.desktop, "Untitled Export", "Nikon-D3500-Shotkit.jpg"), 5))