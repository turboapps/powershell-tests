# The tests for keepersecurity/keeperpasswordmanager and keepersecurity/keeperpasswordmanager-x64 are almost the same except for the shortcut.

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

# Test of `turbo run`.
wait("welcome.png")
run("turbo stop test")
if exists("quit.png"):
    click(Pattern("quit.png").targetOffset(8,49))

# Launch the app.
run('explorer "' + os.path.join(util.start_menu, "Keeper Security, Inc", "Keeper Password Manager.lnk") + '"') # Need to wrap the path for comma.

# Basic operations.
click(Pattern("welcome.png").targetOffset(-90,0))
click(Pattern("login_email.png").targetOffset(-184,50))
paste(username)
type(Key.ENTER)

# It might be stuck at MFA.
if exists("login_password.png"):
    wait("login_password.png")
    paste(password)
    type(Key.ENTER)
    click(Pattern("get_started.png").targetOffset(145,133))
    wait("keeper_window.png")
    type("n", Key.CTRL)
    wait("new.png")
    paste("test")
    click(Pattern("new_top.png").targetOffset(0,37))
    click(Pattern("new_bottom.png").targetOffset(44,0))
    wait(3)
    click(Pattern("new_submit.png").targetOffset(184,-116))
    wait("record.png")
    click(Pattern("record_detail.png").targetOffset(174,-35))
    click("record_detail_delete.png")
    click(Pattern("record_detail_delete_ok.png").targetOffset(175,91))
    wait("keeper_window.png")

# Check "help".
click(Pattern("menu.png").targetOffset(25,-1))
click(Pattern("menu_help.png").targetOffset(-50,-14))
wait("help_url.png")
closeApp("Edge")
click("keeper-title-bar.png")
type("q", Key.CTRL)

# Check if the session terminates.
util.check_running()