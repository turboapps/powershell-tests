script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Test of `turbo run`.
wait("winscp_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "WinSCP.lnk"))
wait("winscp_window.png")

# Basic operations.
type("ftp.adobe.com")
click(Pattern("connect_1.png").targetOffset(24,-13))
click(Pattern("connect_2.png").targetOffset(-47,23))
wait(2)
click(Pattern("connect_3.png").targetOffset(-180,53))
type(Key.ENTER)

# The server might be busy.
retry_quota = 10
while exists("connection_failed.png") and retry_quota > 0:
    wait(30) # Wait for the auto reconnect
    retry_quota -= 1

doubleClick(Pattern("ftp_download_1.png").targetOffset(0,-28))
click(Pattern("ftp_download_2.png").targetOffset(0,29))
type(Key.F5)
wait("ftp_download_3.png")
type(os.path.join(util.desktop, "*.*") + Key.ENTER)
wait(10)
assert(os.path.exists(os.path.join(util.desktop, "version.xml")))

# Check "help".
type(Key.F1)
wait("help_url.png")
closeApp("Edge")
click(Pattern("winscp_menu.png").targetOffset(170,-15)) # To gain focus.
type(Key.F4, Key.ALT)
click(Pattern("save_workspace.png").targetOffset(-60,63))
wait(10)

# Check if the session terminates.
util.check_running()