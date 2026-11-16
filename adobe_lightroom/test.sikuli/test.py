script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(45)

import time
util.pre_test()

# Lightroom 2026-11 redesign: first-run modals open over the main window a few
# seconds after it paints, in no fixed order and not on every launch (App Tests
# 43960251725: "Personalize Your Lightroom" on both launches, the new-style
# "What's New" only on the second, after Local had already been clicked). Close
# whichever shows until none has appeared for `settle` seconds. Polls go through
# SCREEN.exists, which the step-frame hooks don't wrap, so the loop doesn't flood
# the frame cap; the clicks are hooked and each leaves a frame.
#   personalize.png -> keep the Default workspace, "Done" (523,355) off the heading
#   whats_new.png   -> the close X (893,-21) off the heading
#   new_feature.png -> pre-redesign "What's New" close X, kept for older builds
FIRST_RUN_MODALS = [
    ("personalize.png", Pattern("personalize.png").targetOffset(523,355)),
    ("whats_new.png",   Pattern("whats_new.png").targetOffset(893,-21)),
    ("new_feature.png", Pattern("new_feature.png").targetOffset(485,-3)),
    ("got_it.png",      Pattern("got_it.png")),
]
def dismiss_first_run_modals(settle=15, limit=120):
    start = quiet_since = time.time()
    while time.time() - start < limit:
        hit = None
        for image, target in FIRST_RUN_MODALS:
            if SCREEN.exists(image, 0):
                hit = (image, target)
                break
        if hit:
            click(hit[1])
            waitVanish(hit[0], 10)
            quiet_since = time.time()
        elif time.time() - quiet_since >= settle:
            return
        else:
            time.sleep(1)

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test turbo run
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(10)
paste('turbo run lightroom --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test' + util.read_extra())
wait(5)
type(Key.ENTER)
# First launch of the freshly pulled 3.6 GB image. The 45 s ambient timeout is
# not enough: in App Tests run 42303167629 (xvm 26.11.2) the FAILED frame scores
# 0.93 against lightroom_window.png - the window painted just past the deadline,
# with a "What's New" modal on top - and the passes in the same sweep spent up
# to ~100 s between this launch and the following turbo stop. Same shape as the
# keeper/libreoffice cold-launch budgets.
wait("lightroom_window.png", 120)
if exists("adobe_login_signout_others.png",60):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("adobe_login_team.png",10):
    click(Pattern("adobe_login_continue.png").similar(0.80))
dismiss_first_run_modals()
wait("lightroom_window.png")
run("turbo stop test")
closeApp("Command Prompt")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Adobe Lightroom.lnk"))
wait("lightroom_window.png", 120)
dismiss_first_run_modals()
wait("lightroom_window.png")
click("local.png")
if exists("got_it.png",10):
    click("got_it.png")
if exists("got_it.png",10):
    click("got_it.png")
click("browse.png")
click("local_open.png")
wait("import_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "Nikon-D3500-Shotkit.NEF"))
type(Key.ENTER)
wait("local_photo.png")
click("edit.png")
wait(2) # Wait for Edit panel to load.
click(Pattern("exposure.png").targetOffset(100,11))
wait(2)
type("5" + Key.ENTER)
wait("local_photo_edited.png")
click("export.png")
wait(30) # This can be slow.
click("export_jpg.png")
wait("export_location.png")
paste("%USERPROFILE%\\Desktop")
type(Key.ENTER)
click("export_confirm.png")

# Check "help".
type(Key.F1)
wait("help_url.png")
if App("Edge").isRunning(10):
    util.close_app("Edge")
wait(10)
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()

# Export might be slow.
assert(util.file_exists(os.path.join(util.desktop, "Nikon-D3500-Shotkit.jpg"), 5))