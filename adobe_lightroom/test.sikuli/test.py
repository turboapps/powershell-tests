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

# Test of `turbo run`.
wait("lightroom_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Adobe Lightroom.lnk"))
click("adobe_login.png") # To gain focus.
util.adobe_cc_login(username, password)
if exists("new_feature.png"):
    click(Pattern("new_feature.png").targetOffset(485,-3))
if exists("splash.png"):
    click(Pattern("splash.png").targetOffset(408,-178))
if exists("new_feature.png"): # Not sure which one appears first.
    click(Pattern("new_feature.png").targetOffset(485,-3))

# Basic operations.
wait("lightroom_window.png")
click("add_photos.png")
wait("import_location.png")
type(os.path.join(script_path, os.pardir, "resources", "Nikon-D3500-Shotkit.NEF") + Key.ENTER)
wait("cloud_sync.png")
click("cloud_sync_ok.png")
click("add_photos_add.png")
doubleClick("photo.png")
click("edit.png")
wait(2) # Wait for Edit panel to load.
click(Pattern("exposure.png").targetOffset(107,-12))
wait(2)
type("5" + Key.ENTER)
wait("photo_edited_thumbnail.png")
click("export.png")
click("export_jpg.png")
wait("export_location.png")
type("%USERPROFILE%\\Desktop" + Key.ENTER)
click("export_confirm.png")

# Check "help".
type(Key.F1)
util.close_firewall_alert()
wait("help_url.png")
closeApp("Edge")
wait(10)

# Clean up for the next test.
click("photo_edited_thumbnail.png")
type(Key.DELETE)
click("delete.png")
wait(10)
click(Pattern("creative_cloud.png").targetOffset(65,-1))
wait("delete_synced.png")
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()

# Export might be slow.
assert(util.file_exists(os.path.join(util.desktop, "Nikon-D3500-Shotkit.jpg"), 5))