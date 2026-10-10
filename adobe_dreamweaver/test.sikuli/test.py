script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
save_path = include_path = os.path.join(util.desktop, "test", "test")

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
paste('turbo run dreamweaver --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test' + util.read_extra())
type(Key.ENTER)

# Minimize the command prompt
App().focus("Command Prompt")
type(Key.DOWN, Key.WIN)

if exists("introducing.png",90):
    click("introducing.png")
    type(Key.ESC)
if exists("adobe_login_signout_others.png", 20):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
click(Pattern("sync_settings.png").targetOffset(-12,59))
wait("dw_window.png",20)
type("q", Key.CTRL)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Dreamweaver"))

# Dreamweaver's startup dialogs (the "Introducing" overlay, Sync Settings) can
# leave the foreground on an invisible 1x1 window instead of Dreamweaver:
# App.focusedWindow() = R[0,0 1x1] while the main window is R[0,0 1920x1040].
# The screen looks exactly like a good run, but every keystroke goes to that
# window - the ESC that should close the overlay, the Ctrl+N that should open
# New Document. So each key press below is preceded by a click on Dreamweaver's
# caption (the empty strip between the menus and the workspace switcher),
# checked for its effect, and retried, logging the foreground window on a miss.
def dw_activate():
    click(Location(1500, 1056))  # SABOTAGE: empty taskbar, never activates Dreamweaver
    wait(1)

def dw_log_miss(what, attempt):
    try:
        Debug.user("dreamweaver: %s (attempt %d); foreground window %s"
                   % (what, attempt, App.focusedWindow()))
    except:
        Debug.user("dreamweaver: %s (attempt %d) (%s)" % (what, attempt, sys.exc_info()[1]))

# Basic operations.
if exists("introducing.png",90):
    click("introducing.png")
    type(Key.ESC)
click(Pattern("sync_settings.png").targetOffset(-12,59)) # To gain the focus.
click(Pattern("sync_settings.png").targetOffset(-12,59))
for attempt in range(1, 4):
    if not exists("introducing.png", 3):
        break
    dw_log_miss("'Introducing' overlay still up", attempt)
    dw_activate()
    type(Key.ESC)
    waitVanish("introducing.png", 10)
wait("dw_window.png",20)
wait(3)
for attempt in range(1, 4):
    dw_activate()
    type("n", Key.CTRL)
    if exists("new.png", 20):
        break
    dw_log_miss("no New Document after Ctrl+N", attempt)
click(Pattern("new.png").targetOffset(0,4))
wait("new_template.png",20)
wait(3)
type(Key.ENTER)
wait("code.png",60)
click("code.png")
type("s", Key.CTRL)
wait("save_location.png",20)
wait(3)
paste(save_path)
wait(3)
type(Key.ENTER)
wait(10)
type("w", Key.CTRL + Key.SHIFT)
wait(3)
type(Key.ENTER)
wait(3)
type("o", Key.CTRL)
wait("open_location.png",20)
wait(3)
paste(save_path)
wait(3)
type(Key.ENTER)
wait("code.png",20)

# Check "help".
type(Key.F1)
if exists("help-sign-in.png",30):
    click("help-sign-in.png")
wait("help_url.png",15)
util.close_app("Edge")
wait(10)
type("q", Key.CTRL)
wait(10)

# Check if the session terminates.
util.check_running()