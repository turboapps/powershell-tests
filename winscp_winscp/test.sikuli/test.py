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
click("connect_1.png")
click(Pattern("connect_2.png").targetOffset(-47,23))
wait(2)
type(Key.TAB)
type(Key.TAB)
type("ftp.dlptest.com")
type(Key.TAB)
type(Key.TAB)
type("dlpuser")
type(Key.TAB)
type("rNrKYTX9g7z3RgJRmxWuGHbeu")
type(Key.ENTER)

# The server might be busy.
wait("ftp_download_1.png",60)
click("ftp_download_1.png")
type(Key.F5)
wait("ftp_download_3.png")
type(os.path.join(util.desktop, "image.jpg") + Key.ENTER)
wait(10)
assert(os.path.exists(os.path.join(util.desktop, "image.jpg")),90)

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