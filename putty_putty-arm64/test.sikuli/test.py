script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import subprocess
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
host = credentials.get("host")
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait("putty_window.png")
run("turbo stop test")

# Launch the telnet server
hk_telnet_server = os.path.join(script_path, os.pardir, "resources", "hk-telnet-server.exe")
subprocess.Popen("turbo run base -n=telnet --network=test --startup-file=" + hk_telnet_server + " -d")
wait("telnet-start.png")
click("telnet-start.png")
            
# Launch the app.
run("explorer " + os.path.join(util.start_menu, "PuTTY (64-bit)", "PuTTY.lnk"))
wait("putty_window.png")

# Check "help".
click(Pattern("putty_window.png").targetOffset(-88,204))
click("help.png")
type(Key.F4, Key.ALT)

# Basic operations.
click(Pattern("putty_window.png").targetOffset(-53,-100))
type(host)
click(Pattern("putty_window.png").targetOffset(57,-56))
type(Key.ENTER)

wait("username.png")
type(username)
wait(3)
type(Key.ENTER)
wait("password.png")
type(password)
wait(3)
type(Key.ENTER)
# Not sure why but the first login fails
if exists("invalid-login.png"):
    type(username)
    wait(3)
    type(Key.ENTER)
    wait("password.png")
    type(password)
    wait(3)
    type(Key.ENTER)
wait("logged_in.png")
type(Key.F4, Key.ALT)
click(Pattern("close.png").targetOffset(23,38))
click("telnet-exit.png")
run("turbo stop telnet")

# Check if the session terminates.
util.check_running()