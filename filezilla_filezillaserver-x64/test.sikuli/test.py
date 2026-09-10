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
# App().focus("cmd") here ran before the container existed, so it was a silent
# no-op, and the 10 s that followed was the last tight wait left in this file.
# In App Tests run 34419239508 the container's console painted 6.183 s after the
# Turbo CLI logged its command line -- measured in the VM logs: session host
# +2.624 s, conhost +4.621 s, cmd.exe +5.402 s, ShowWindow +5.543 s, last
# WriteConsole +6.183 s -- and turbo.exe's own cold start sits in front of that,
# unlogged. The wait expired about half a second short: cmd_window.png scores
# 0.9877 on the very frame captured at the FindFailed. Poll and re-focus instead.
#
# The window matcher is "@cmd#", not "cmd": a bare "cmd" also matches the
# harness's own console window, so it can focus the wrong one. The token comes
# from -n=cmd above and appears only in the container console's title.
if not util.focus_and_wait("@cmd#", "cmd_window.png", attempts=12, poll=5):
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