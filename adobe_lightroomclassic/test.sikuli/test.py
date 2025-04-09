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

# Test of `turbo run`.
if exists("share_data.png"):
    click(Pattern("share_data.png").targetOffset(194,72))
if exists("whats_new.png"):
    click("whats_new_close.png")
if exists(Pattern("welcome.png").targetOffset(71,3)):
    click(Pattern("welcome.png").targetOffset(71,3))
if exists("getting_started.png"):
    click(Pattern("getting_started.png").targetOffset(186,-18))
click("adobe_login.png")
type(Key.F4, Key.ALT)
wait(15)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Adobe Lightroom Classic.lnk"))
if exists("share_data.png"):
    click(Pattern("share_data.png").targetOffset(194,72))
if exists("whats_new.png"):
    click("whats_new_close.png")
if exists(Pattern("welcome.png").targetOffset(71,3)):
    click(Pattern("welcome.png").targetOffset(71,3))
if exists("getting_started.png"):
    click(Pattern("getting_started.png").targetOffset(186,-18))
util.adobe_cc_login(username, password)

# Basic operations.
wait("lightroomcc_window.png")
type("i", Key.CTRL + Key.SHIFT)
click("import_select_source.png")
click(Pattern("import_select_source_menu.png").targetOffset(-8,7))
wait("import_location.png")
type(os.path.join(script_path, os.pardir, "resources") + Key.ENTER)
wait(2)
type(Key.ENTER)
wait("import_thumbnail.png")
click("import_import.png")
wait("import_done.png")
type("d")
wait(2) # Wait for Edit panel to load.
if exists("develop_mode.png"):
    click(Pattern("develop_mode.png").targetOffset(181,-96))
if exists("point_color.png"):
    click(Pattern("point_color.png").targetOffset(219,-54))
type("r")
wait(2)
type("x")
wait(2)
type(Key.ENTER)
wait("adjusted.png")
type("e", Key.CTRL + Key.SHIFT)
wait("export.png")
type(Key.ENTER)

# Check "help".
type(Key.F1)
wait("help_url.png")
closeApp("Edge")
wait(10)
if exists("import_select_source.png"):
    wait(2)
    click("import_cancel.png")
type("q", Key.CTRL)
click(Pattern("quit.png").targetOffset(101,28))
wait(30)

# Check if the session terminates.
util.check_running()

# Export might be slow.
assert(util.file_exists(os.path.join(util.desktop, "Untitled Export", "Nikon-D3500-Shotkit.jpg"), 5))