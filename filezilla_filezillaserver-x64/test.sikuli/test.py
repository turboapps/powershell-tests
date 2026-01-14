script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import subprocess
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

# Minimize the sikulix console
if exists("sikulix-console.png",15):
    click("sikulix-console.png")
    wait(2)
    type(Key.DOWN, Key.WIN)

# Test of `turbo run`.
App("FileZilla Server").focus()
wait("connect_button.png",60)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "FileZilla Server", "Administer FileZilla Server.lnk"))

# Basic operations.
wait("app-launched.png",60)
wait(5)
type("c")
click(Pattern("connect_port.png").targetOffset(11,92))
click(Pattern("connect_fingerprint.png").targetOffset(226,6))
wait("server_window.png")
type("i", Key.CTRL)
wait("file_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "config.xml"))
wait(3)
type(Key.ENTER)
wait("import.png")
type(Key.ENTER)

# Test ftp.
subprocess.Popen("turbo run base -n=cmd --network=test --startup-file=cmd -d")
App().focus("cmd")
wait("cmd_window.png",10)
wait(3)
paste("ftp 127.0.0.1")
wait(3)
type(Key.ENTER)
wait("ftp_user.png")
type("test" + Key.ENTER)
wait("ftp_password.png")
type(Key.ENTER)
wait("ftp_ok.png")
type("quit" + Key.ENTER)
wait(2)
type("exit" + Key.ENTER)

App("FileZilla Server").focus()
click(Pattern("server_window.png").targetOffset(75,-10))
type("d", Key.CTRL)
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()