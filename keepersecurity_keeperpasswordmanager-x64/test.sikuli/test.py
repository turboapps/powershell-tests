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
run('explorer "' + os.path.join(util.start_menu, "Keeper Password Manager.lnk") + '"') # Need to wrap the path for comma.

# Basic operations.
wait("welcome.png")
wait(10)
click(Pattern("welcome.png").targetOffset(-90,0))
click(Pattern("login_email.png").targetOffset(-184,50))
paste(username)
type(Key.ENTER)

# It might be stuck at MFA or device approval. When the master password screen
# never appears the whole vault section below is skipped and the test still
# reports a pass, so the record coverage can go missing without anyone noticing
# - say out loud which path we took, and name device approval when that is why.
#
# As of 2026-09-04 that is where every run lands and the vault section below is
# UNREACHABLE. Keeper answers this account with "Device Approval Needed" and
# wants 2-step verification; every containerised run is a device it has never
# seen, and the harness wipes the sandbox that would have remembered one. So
# the record create/delete steps have not run in a long time - treat their
# captures as unverified against the current build. Left alone for now:
# reaching them needs the device approved without a human, either by entering
# the 2FA code from the test or by dropping the approval requirement on the
# account.
if exists("login_password.png"):
    Debug.user("master password screen shown - running the vault record checks")
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
elif exists("device_approval.png", 0):
    Debug.user("Keeper is asking to approve this device - SKIPPED the vault record checks")
else:
    Debug.user("no master password screen - SKIPPED the vault record checks")

# Check "help".
click(Pattern("menu.png").targetOffset(25,-1))
click(Pattern("menu_help.png").targetOffset(-50,-14))
# Edge starts cold inside the isolate container and the docs page is heavy, so
# the default 30 s is too tight - run 33849047386 missed the URL by under 7 s.
wait("help_url.png", 60)
if App("Edge").isRunning(10):
    util.close_app("Edge")
click("keeper-title-bar.png")
type("q", Key.CTRL)

# Check if the session terminates.
util.check_running()