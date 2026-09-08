script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import subprocess
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

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
subprocess.Popen("turbo run base -n=cmd --network=test --startup-file=cmd -d" + util.read_extra())
# `turbo run base -n=cmd ... -d` above is asynchronous, so this wait has to
# cover the container being created before the console can even appear, and
# App().focus("cmd") runs before that window exists, so it is a silent no-op
# that nothing retries. 10 s has held so far because a bare cmd container is
# much cheaper to start than the Edge one that made the same shape flaky in
# opensearch (App Tests 34097555049 / 34097578991), but the margin is the
# same one and nothing here needs it to be this tight. Poll and re-focus.
if not util.focus_and_wait("cmd", "cmd_window.png", attempts=9, poll=10):
    wait("cmd_window.png")  # still absent: fail with the usual FindFailed
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