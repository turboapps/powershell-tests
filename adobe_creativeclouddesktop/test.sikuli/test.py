script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import time
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
paste('turbo run photoshop --using=creativeclouddesktop,isolate-edge-wc --isolate=merge-user --offline --enable=disablefontpreload --name=test' + util.read_extra())
type(Key.ENTER)

# Minimize the command prompt
App().focus("Command Prompt")
type(Key.DOWN, Key.WIN)

if exists("adobe_login_signout_others.png",90):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("adobe_login_team.png",10):
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("grafx-warning.png",15):
    click(Pattern("grafx-warning.png").targetOffset(255,11))
wait("photoshop-menu-bar.png",15)
run("turbo stop test")
wait(20)

# Launch the app.
setAutoWaitTimeout(30)
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Photoshop"))
# The relaunched Photoshop can take well over 90 s to paint its Home page: the
# window comes up with grey placeholder bars and the "Welcome to Photoshop"
# heading lands later. Keep waiting while the Photoshop window is on screen,
# and give up only if it goes away or Home never paints.
#
# The relaunch can also land on Adobe's "You've reached your device activation
# limit - Sign out of another device to continue" modal, the same one handled
# after the first launch above. Validation run 42567205032 sat on it for the
# whole 300 s (adobe_login_signout_others.png scores 0.79 in every frame from
# ~2 min in) because only the first launch looked for it. Watch for it during
# the Home wait and clear it the same way.
def wait_relaunch_home(timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        if exists("Welcome.png", 0):
            return
        if exists("adobe_login_signout_others.png", 0):
            Debug.user("relaunch: device activation limit modal, signing out another device")
            click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
            click(Pattern("adobe_login_continue.png").similar(0.80))
        wait(2)
    wait("Welcome.png", 1)  # still not up: raise the usual FindFailed + FAILED frame

wait_relaunch_home()
wait("photoshop-menu-bar.png")
if exists("grafx-warning.png",20):
    click(Pattern("grafx-warning.png").targetOffset(255,11))
# Basic operations.
type("o", Key.CTRL)
if exists("on-your-computer.png",30):
    click("on-your-computer.png")
wait("file_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "sample.png"))
type(Key.ENTER)
wait(5)
type("w", Key.ALT + Key.CTRL + Key.SHIFT)
wait("export-button.png")
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