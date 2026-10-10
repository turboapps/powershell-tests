script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import time
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(60)

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
type('turbo run characteranimator --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test' + util.read_extra())
type(Key.ENTER)
wait("title-bar.png",60)
if exists("adobe_login_signout_others.png", 20):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
wait("lacy_puppet.png",60)
wait(10)
type("q",Key.CTRL)
wait(5)
closeApp("Command Prompt")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Character Animator"))
wait("title-bar.png")

# Basic operations.
setAutoWaitTimeout(20)
wait("lacy_puppet.png")
click(Pattern("lacy_puppet.png").targetOffset(-3,-3))
# Wait for the scene to finish loading before asking for an export. Opening the
# puppet shows a black stage with a 'Preparing "Lacy Starter"' and then a
# 'Preparing scene' toast; on the CI VMs (software rendering) that takes longer
# than the fixed 10 s this used to wait, and a click on the quick-export button
# during it is silently ignored - the export panel never opens. scene_ready.png
# is a static piece of the rendered background (the tree stump), which is only
# on screen once the scene has been drawn.
#
# Two app failures show up here on the CI VMs (Microsoft Basic Render Driver, no
# GPU), and both block the UI: Character Animator's own "GPU Error ... HRESULT
# error" modal, and its crash reporter ("Character Animator.exe has encountered
# a problem and needs to close"). Name them in the failure instead of timing
# out at an export image a minute later.
def fail_on_app_error():
    if exists(Pattern("app_crash.png").similar(0.9), 0):
        raise FindFailed("characteranimator: Character Animator crashed (Adobe error-report dialog is up)")
    if exists(Pattern("gpu_error.png").similar(0.9), 0):
        raise FindFailed("characteranimator: Character Animator GPU Error modal is up (Microsoft Basic Render Driver)")

scene_ready = Pattern("scene_ready.png").similar(0.95)
deadline = time.time() + 180
while not exists(scene_ready, 5):
    fail_on_app_error()
    if time.time() > deadline:
        raise FindFailed("characteranimator: the Lacy scene was not drawn within 180 s")
wait(3)
fail_on_app_error()
# export.png is the blue "Export" pill of the quick-export panel. At the default
# 0.7 it also matches the blue "Record face and voice" pill under the stage
# (0.73), so a panel that had not opened turned into a click on Record and the
# test failed a minute later at the mp4 assert. 0.9 separates the two.
export = Pattern("export.png").similar(0.9)
click(Pattern("quick-export-button.png").targetOffset(1,1))
if not exists(export, 30):
    fail_on_app_error()
    Debug.user("characteranimator: export panel did not open, clicking quick-export again")
    click(Pattern("quick-export-button.png").targetOffset(1,1))
    wait(export, 30)
click(export)
wait(10)
assert(util.file_exists(os.path.join(os.environ['USERPROFILE'], "Documents\\Adobe\\Character Animator\\Scene - Lacy Starter.mp4"), 5))
# A finished export opens File Explorer on Documents\Adobe\Character Animator,
# and that window takes the foreground, so a bare Ctrl+Q went to Explorer and
# Character Animator never quit (check_running: still Running after 60 s).
# Bring the app back first. Its title is "Adobe Character Animator 2026"; the
# Explorer window is just "Character Animator", so the prefix tells them apart.
# Explorer can open late (run 38093026114: it was still painting a blank frame
# when Ctrl+Q went out and took the foreground straight back), so a single
# refocus is not enough: re-focus and re-send Ctrl+Q until the app's window is
# gone. A Ctrl+Q that reaches an app that is already closing is harmless.
wait(5)
assert(util.activate_app_window("Adobe Character Animator", 10))
for attempt in range(4):
    if not App().focus("Adobe Character Animator").isValid():
        break
    if attempt:
        Debug.user("characteranimator: still open after Ctrl+Q, refocusing and sending it again (attempt %d)" % (attempt + 1))
    wait(2)
    type("q",Key.CTRL)
    wait(15)

# Check if the session terminates.
util.check_running()