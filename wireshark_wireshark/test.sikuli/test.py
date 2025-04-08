script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# Test of `turbo run`.
wait("wireshark_window.png")
run("turbo stop test")

# Install npcap
run("explorer " + os.path.join(util.desktop, "installer.exe"))
wait("npcap-agree.png")
click("npcap-agree.png")
click("npcap-install.png")
wait(30)
click("npcap-next.png")
click("npcap-finish.png")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Wireshark.lnk"))
wait("wireshark_window.png")

# Basic operations.
if exists ("grey-ethernet.png",5):
    doubleClick("grey-ethernet.png")
if exists ("blue-ethernet.png",5):
    doubleClick("blue-ethernet.png")
wait("menu.png")
wait(2)
click(Pattern("menu.png").targetOffset(12,2))
click(Pattern("restart_capture.png").targetOffset(39,37))
wait(5)
click(Pattern("menu.png").targetOffset(-11,2))
wait(Pattern("captured.png").similar(0.39))

# Check "help".
type(Key.F1)
wait("help.png")
closeApp("Edge")
wait(5)
type(Key.F4, Key.ALT)
click(Pattern("quit.png").targetOffset(16,30))
wait(10)

# Check if the session terminates.
util.check_running()