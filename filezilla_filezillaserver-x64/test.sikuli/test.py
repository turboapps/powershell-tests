script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
util.close_firewall_alert()
App("FileZilla Server").focus()
wait("connect_button.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "FileZilla Server", "Administer FileZilla Server.lnk"))

# Alert might be hidden by other windows.
if exists("alert_taskbar.png"):
    click("alert_taskbar.png")
util.close_firewall_alert()

# Basic operations.
click("connect_button.png")
click(Pattern("connect_port.png").targetOffset(11,92))
click(Pattern("connect_fingerprint.png").targetOffset(-14,12))
wait("server_window.png")
type("i", Key.CTRL)
wait("file_location.png")
type(os.path.join(script_path, os.pardir, "resources", "config.xml") + Key.ENTER)
wait("import.png")
type(Key.ENTER)

# Test ftp.
App().focus("cmd")
wait("cmd_window.png")
type("ftp 127.0.0.1" + Key.ENTER)
wait("ftp_user.png")
type("test" + Key.ENTER)
wait("ftp_password.png")
type(Key.ENTER)
wait("ftp_ok.png")
type("quit" + Key.ENTER)

click("server_taskbar.png")
click(Pattern("server_window.png").targetOffset(75,-10))
type("d", Key.CTRL)
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()