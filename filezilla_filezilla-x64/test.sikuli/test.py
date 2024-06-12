# The tests for filezilla/filezilla and filezilla/filezilla-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Test of `turbo run`.
wait("filezilla_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "FileZilla FTP Client", "FileZilla.lnk"))
click(Pattern("filezilla_window.png").targetOffset(-327,16))

# Basic operations.
type("ftp.adobe.com" + Key.ENTER)

# The server might be busy.
retry_quota = 10
while not exists("tls_warning.png") and retry_quota > 0:
    wait(10)
    type("r", Key.CTRL)
    retry_quota -= 1

click(Pattern("tls_warning.png").targetOffset(45,75))
wait(5)
doubleClick(Pattern("ftp_download_1.png").targetOffset(0,-28))
rightClick(Pattern("ftp_download_2.png").targetOffset(0,29))
click(Pattern("ftp_download_3.png").targetOffset(0,-19))
wait(Pattern("download_successful.png").similar(0.80), 40)
wait(10)
assert(os.path.exists(os.path.join(os.environ["USERPROFILE"], "version.xml")))

# Check "help".
click(Pattern("menu.png").targetOffset(59,0))
click("menu_help.png")
util.close_firewall_alert()
wait("help_url.png")
closeApp("Edge")
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()