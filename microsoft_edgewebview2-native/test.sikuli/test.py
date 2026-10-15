script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)
import subprocess

# Power BI is installed natively; the executor launched it in a base container named
# "test" and recorded the command line in launch.txt (NativeTest.ps1 Start-NativeApp).
# The relaunch goes through the same container, never the Start menu shortcut, which
# would start the native Power BI outside it.
def launch(*args):
    with open(os.path.join(script_path, os.pardir, "launch.txt")) as f:
        command, app_args = (f.read().splitlines() + ["", ""])[:2]
    subprocess.Popen(command + " -d -- " + " ".join([app_args] + ['"%s"' % a for a in args]))

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
# Exit with error code if the WebView2 layer is not working.
if exists("update-required.png"):
    sys.exit(1)
wait("home_button.png",60)
wait(10)
click(Pattern("close_pbi.png").targetOffset(42,-1))
wait(5)
if exists(Pattern("red_x_click.png").targetOffset(42,1)):
    click(Pattern("red_x_click.png").targetOffset(42,1))
wait(5)

# Launch the app.
util.wait_app_quiet("PBIDesktop.exe")
launch()
# Exit with error code if the WebView2 layer is not working.
if exists("update-required.png"):
    sys.exit(1)
wait("home_button.png",60)
wait(10)
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()