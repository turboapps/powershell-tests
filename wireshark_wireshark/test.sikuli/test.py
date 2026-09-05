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
# click() waits for the enabled "Next >" (a greyed one does not match), so this
# also covers an install slower than 30 s.
click("npcap-next.png")
# In CI the single Next click has been dropped with the button enabled and the
# installer left on "Installation Complete" (applab run 33849047386, also seen
# on xvm 26.9.1/26.9.20). Check the outcome and re-click instead of trusting
# one blind click; the Finish click below stays the assertion.
for _ in range(3):
    if exists("npcap-finish.png", 15):
        break
    if exists("npcap-next.png", 2):
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
if App("Edge").isRunning(10):
    util.close_app("Edge")
wait(5)
type(Key.F4, Key.ALT)
click(Pattern("quit.png").targetOffset(16,30))
wait(10)

# Check if the session terminates.
util.check_running()