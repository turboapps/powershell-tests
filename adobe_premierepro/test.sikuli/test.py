script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Wait for the Home screen, getting Premiere's "System Compatibility Report" out
# of the way if it comes up first.
#
# From 26.5 Premiere checks the GPU at startup, and on a pool VM (no GPU) it
# raises that report as a modal over the main window: "No graphics processor
# suitable for GPU-accelerated rendering was found on this system". Home is not
# drawn behind it, so pr_window.png cannot match until "Continue with known
# issues" is clicked. The report is an ordinary startup step, not a fault - the
# app runs fine on the CPU renderer afterwards - and it can come up on any launch,
# so this is checked on both. Nothing is clicked when the report does not appear.
#
# The report is probed with SCREEN.exists, which the step-frame hooks do not
# wrap, so polling it does not store a frame per poll; the click still does.
compat_continue = Pattern("compat_continue.png").similar(0.80)
def wait_pr_window(timeout, slice=10):
    waited = 0
    while waited < timeout:
        if exists("pr_window.png", slice):
            return
        waited += slice
        if SCREEN.exists(compat_continue, 0):
            Debug.user("System Compatibility Report up at %d s; continuing with known issues" % waited)
            click(compat_continue)
    wait("pr_window.png", 10)

# Wait for the sequence timeline after the project opens, answering Premiere's
# "No output device is available" prompt when it comes up first.
#
# A pool VM has no audio output device, so Premiere asks whether to open the
# Audio Hardware preference while it loads the project. The prompt is modal and
# the timeline is not drawn behind it until it is answered ("No"). It takes a
# variable time to appear after the convert prompt's OK: 12.6 s, 21 s and 29.2 s
# in the three passes of 2026-10-17 (runs 38988956810, 38988953618, 38988242019),
# so the old fixed 30 s exists() missed it in 38988960389 and timeline.png then
# failed behind the still-open prompt. The prompt and the "Essential Graphics
# panel has been renamed" notice are probed with SCREEN.exists (unhooked, no step
# frame per poll) between timeline polls; nothing is clicked when they are absent.
def wait_timeline(timeout, slice=10):
    waited = 0
    while waited < timeout:
        if exists("timeline.png", slice):
            return
        waited += slice
        if SCREEN.exists("no_output_device.png", 0):
            Debug.user("No output device prompt up at %d s; answering No" % waited)
            click(Pattern("no_output_device.png").targetOffset(137,53))
        if SCREEN.exists("panel_rename.png", 0):
            click(Pattern("panel_rename_close.png").targetOffset(-2,-10))
    wait("timeline.png", 10)

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test turbo run
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
paste('turbo run premierepro --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test' + util.read_extra())
wait(2)
type(Key.ENTER)

# minimize the command prompt
cmd_prompt = App().focus("Command Prompt")
if cmd_prompt.isValid():
    type(Key.DOWN, Key.WIN)

if exists("adobe_login_signout_others.png",180):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("adobe_login_team.png",10):
    click(Pattern("adobe_login_continue.png").similar(0.80))

wait_pr_window(60)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Premiere Pro"))

# Basic operations.
wait_pr_window(180)
click("pr_window.png") # To gain focus.
type("o", Key.CTRL)
wait("location.png")
paste(os.path.join(script_path, os.pardir, "resources", "create-project-import-media", "create-project-import-media-step1.prproj"))
wait(2)
type(Key.ENTER)
wait("convert_prompt.png")
click("ok-button.png")
wait_timeline(180)

# Check "help".
type(Key.F1)
wait("help_url.png")
util.close_app("Edge")
wait(10)
click("timeline.png") # Gain focus.
type(Key.F4, Key.ALT)
if exists("dont-save.png",10):
    click("dont-save.png")
wait(10)

# Check if the session terminates.
util.check_running()