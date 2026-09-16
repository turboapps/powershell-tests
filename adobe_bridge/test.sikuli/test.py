script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
# normpath, because this goes into Adobe Bridge's path bar and Bridge will not
# resolve a ".." segment: os.path.join leaves
# "...\adobe_bridge\test.sikuli\..\resources", Bridge rejects it, the bar snaps back
# to the folder it was already showing and the test then looks for the fox
# thumbnail on the Desktop. Runs 35011281602 and 35005251292 (different refs,
# hours apart) both show the unresolved path typed into the bar and the view
# still on Desktop 45 s later.
resources = os.path.normpath(os.path.join(script_path, os.pardir, "resources"))
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(45)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test turbo run
#
# Creative Cloud does not stay closed. Seconds after launch_adobe_cc closes it,
# it puts its own window back up - "Initializing Creative Cloud...", titled
# "(Not Responding)" - on top of everything, and it holds the foreground while
# it is wedged there. The command below was then typed into that window
# instead of the console, and the test died 45 s later at bridge_window.png
# with the console still sitting at a bare prompt: runs 35011268672 and
# 35011296309, both with an identical step frame. So take the keyboard back
# before typing, and check the line actually took the text instead of
# assuming it did. cmd_prompt.png is the prompt alone, so it matches whatever
# the line holds; cmd_empty_line.png is the prompt PLUS the blank space after
# it, so it matches only while the line is still empty - that is the witness.
turbo_run = ('turbo run bridge --using=isolate-edge-wc,creativeclouddesktop'
             ' --offline --enable=disablefontpreload --name=test' + util.read_extra())
for attempt in range(3):
    # Take the keyboard back from whatever is in front (focus_console verifies
    # the console really is the foreground window, which App().focus does not),
    # then clear the line so a retry cannot leave two copies of the command.
    util.focus_console("cmd_prompt.png")
    type(Key.ESC)
    util.paste_text(turbo_run, 2)
    if exists("cmd_empty_line.png", 2) is None:
        break
    Debug.user("turbo run: the line is still empty, the paste was lost (attempt %d of 3)" % (attempt + 1))
type(Key.ENTER)
if exists("adobe_login_signout_others.png",60):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("adobe_login_team.png",10):
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("gpu_warning.png"):
    click(Pattern("gpu_warning.png").targetOffset(179,88))
if exists("bridge_new.png"):
    type(Key.ESC)
wait("bridge_window.png")
run("turbo stop test")
closeApp("Command Prompt")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Bridge"))
if exists("gpu_warning.png",60):
    click(Pattern("gpu_warning.png").targetOffset(179,88))
if exists("bridge_new.png"):
    type(Key.ESC)
wait("bridge_window.png")

# Basic operations.
click(Pattern("bridge_window.png").targetOffset(-119,27))
paste(resources)  # Bridge cannot take relative paths.
wait(2)
type(Key.ENTER)
wait(5)
click("red-fox-thumbnail.png")
click("Output-menu.png")
rightClick("fox-content.png")
click("add-to-output-doc.png")
wait("output-doc.png")
click("export-pdf.png")
wait("save-pdf.png")
wait(10)
paste("%userprofile%\\desktop\\fox.pdf")
wait(2)
type(Key.ENTER)
wait("fox-output.png")
util.close_app("Edge")

# Check "help".
type(Key.F1)
if exists("help-sign-in.png",15):
    click("help-sign-in.png")
wait("bridge-user-guide.png")
util.close_app("Edge")
wait(10)
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()
