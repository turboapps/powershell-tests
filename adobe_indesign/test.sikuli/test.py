script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import subprocess
import time
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
save_path = include_path = os.path.join(util.desktop, "test.indd")

# Wait for an InDesign launch to reach its Home screen, for as long as the screen
# shows that it is still starting.
#
# InDesign 21.6 under Turbo takes minutes to start, and every fixed budget this
# test had was overtaken by it. App Tests full-suite runs, all on image
# indesign:21.6#be41bf07:
# - run 37826953706 (xvm 26.10.97): the "sign out other devices" prompt came up
#   ~100 s in and was answered, then wait("indesign_window.png",10) gave up
#   while the main frame was up but still empty; the FAILED frame, taken a few
#   seconds later, shows the Home screen.
# - run 37868755768 (xvm 26.10.98): the shortcut relaunch was still on the splash
#   ("Starting up panels...") when wait("indesign_window.png",300) expired, and
#   the screenshot after that shows the empty main frame.
# - run 37868758654 (xvm 26.10.99): the same relaunch took ~270 s and squeaked in.
# The first launch was paying the same cost, hidden inside
# exists("adobe_login_signout_others.png",300), which ran out all 300 s in every
# run where the prompt did not come up.
#
# So poll for the Home screen and keep waiting while either the splash
# (indesign_splash.png) or the empty main frame's menu bar (indesign_frame.png) is
# on screen; give up once neither has been seen for `grace` seconds, so a launch
# that never starts reports in a few minutes rather than at the ceiling. The
# Creative Cloud sign-in prompts that can come up on the first launch are
# answered as they appear. Crops: the splash scores 1.00 on the splash and <0.50
# on every other frame; the frame scores 0.94 on the empty frame and <0.26 on the
# desktop and on the sign-in pages.
def wait_indesign_window(ceiling=900, poll=15, grace=180):
    start = time.time()
    last_busy = start
    while time.time() - start < ceiling:
        if exists("indesign_window.png", poll):
            Debug.user("InDesign window up %d s after the launch" % (time.time() - start))
            return
        # Unhooked lookups for the side probes, so a long launch costs one step
        # frame per poll rather than one per probe.
        if SCREEN.exists("adobe_login_signout_others.png", 0) is not None:
            click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
            click(Pattern("adobe_login_continue.png").similar(0.80))
            last_busy = time.time()
            continue
        if SCREEN.exists("adobe_login_team.png", 0) is not None:
            click(Pattern("adobe_login_continue.png").similar(0.80))
            last_busy = time.time()
            continue
        elapsed = time.time() - start
        if (SCREEN.exists("indesign_splash.png", 0) is not None
                or SCREEN.exists("indesign_frame.png", 0) is not None):
            last_busy = time.time()
            Debug.user("InDesign still starting %d s in" % elapsed)
        elif time.time() - last_busy > grace:
            Debug.user("InDesign: no splash or main frame for %d s, %d s in" % (grace, elapsed))
            break
    wait("indesign_window.png", 30)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test turbo run
subprocess.Popen("turbo run indesign --using=creativeclouddesktop,isolate-edge-wc --offline --enable=disablefontpreload --network=test --name=test" + util.read_extra())
wait_indesign_window()
run("turbo stop test")
# The next wait must not match the stopped instance's window (see adobe_incopy,
# where `turbo stop` returned while the dead window was still painted).
assert waitVanish("indesign_window.png", 120), "the stopped InDesign window is still on screen"
closeApp("Command Prompt")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe InDesign"))

# Basic operations.
wait_indesign_window()
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
if exists("save_cc.png"):
    click("save_cc.png")
wait("save_location.png")
paste(save_path)
type(Key.ENTER)
assert(util.file_exists(save_path, 5))
run("explorer " + os.path.join(script_path, os.pardir, "resources", "Save.indd"))
# Save.indd was saved with Hunspell (English: USA) hyphenation, which this image
# does not ship, so InDesign opens it with a "Hyphenation breaks may change"
# warning ahead of the missing-fonts dialog (runs 37661379763 and 37868758654:
# the warning sat on screen for the whole 120 s wait for missing_fonts.png).
# Poll for both, so a run where the warning does not come up costs nothing.
opened = time.time()
while time.time() - opened < 120 and not exists("missing_fonts.png", 5):
    pass  # PROBE: hyphenation warning deliberately not acknowledged
wait("missing_fonts.png",30)
click(Pattern("missing_fonts.png").targetOffset(205,155))
wait("open-doc.png")

# Check "help".
type(Key.F1)
wait("help_url.png")
util.close_app("Edge")
wait(10)
type(Key.F4, Key.ALT)
click(Pattern("save.png").targetOffset(101,25))
wait(10)

# Check if the session terminates.
util.check_running()
