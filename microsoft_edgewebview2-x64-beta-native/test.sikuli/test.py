script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)
import subprocess

# The new Outlook is installed natively; the executor launched it in a base container
# named "test" and recorded the command line in launch.txt (NativeTest.ps1
# Start-NativeApp). The relaunch goes through the same container, never a shortcut,
# which would start the native Outlook outside it.
def launch(*args):
    with open(os.path.join(script_path, os.pardir, "launch.txt")) as f:
        command, app_args = (f.read().splitlines() + ["", ""])[:2]
    subprocess.Popen(command + " -d -- " + " ".join([app_args] + ['"%s"' % a for a in args]))

# The Beta policies must have steered Outlook to the Edge Beta WebView2 runtime: the VM
# also carries the Stable runtime, and a pass on that would say nothing about Beta.
def assert_beta_runtime():
    paths = subprocess.check_output(["powershell", "-NoProfile", "-Command",
        "Get-Process msedgewebview2 -ErrorAction SilentlyContinue | ForEach-Object { $_.Path }"])
    Debug.user("msedgewebview2 processes:\n" + paths)
    assert "Edge Beta" in paths, "Outlook is not running the Edge Beta WebView2 runtime"

setAutoWaitTimeout(40)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait("email-prompt.png")
assert_beta_runtime()
wait(5)
type(Key.F4, Key.ALT)
wait(5)
run("turbo stop test")


# Launch the app.
util.wait_app_quiet("olk.exe")
launch()
wait("email-prompt.png")
click("email-prompt.png")
paste(username)
wait(3)
type(Key.ENTER)
wait("sign_in_password.png",120)
paste(password)
wait(3)
type(Key.ENTER)
wait("yes-all-apps.png",10)
click("yes-all-apps.png")
if exists("sign_in_password.png",10):
    paste(password)
    wait(3)
    type(Key.ENTER)
if exists("sign_in_done.png",10):
    click("sign_in_done.png")
wait("not-interested.png",180)
click("not-interested.png")
wait("new-mail-button.png")
click("new-mail-button.png")
wait("email-to.png")
click("email-to.png")
paste("sandy@gridturbo.onmicrosoft.com")
wait(5)
type(Key.TAB)
wait(3)
type(Key.TAB)
wait(3)
paste("sikulix test email")
type(Key.TAB)
paste("This email can be deleted.")
# Send, and hold the test to the send actually happening.
#
# send-email-button.png used to be the word "Send" on the flat blue button - a
# 71x25 crop that is almost entirely one colour, so the only thing the match had
# to go on was the four thin glyphs. It scored 0.738 on the runs that passed,
# 0.038 over SikuliX's 0.7 default. In App Tests run 35806302540 the compose
# surface painted its label and its paper-plane icon a weight lighter than usual
# (the button came out 5 px narrower; everything outside the compose - the Home
# ribbon, the message list, the subject and body text - was pixel-identical to
# the passing runs), which took the same on-screen button down to 0.426 and
# FindFailed on a Send button that was right there, enabled, over a fully
# addressed message. The reference is now the paper-plane glyph inside the
# button: a shape rather than text, 0.95-0.97 against both renderings, and 0.46
# against the New mail button - the one other blue-button-with-white-icon on
# screen, and the one the click leads back to.
if not util.click_until_gone("send-email-button.png"):
    raise FindFailed("send-email-button.png: compose still open after Send")
wait(5)
click("calendar-button.png")
wait("today-icon.png")
click("print-button.png")
wait("blue-print-button.png")
wait(10)
click("blue-print-button.png")
wait("second-blue-print-button.png")
wait(5)
type(Key.ESC)
wait(5)
type(Key.ESC)
wait(5)
type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates.
util.check_running()

# The Edge DLLs (Edge, Edge Beta, EdgeWebView) must load from the native install, not
# be faulted into the container's sandbox.
util.assert_no_faulted_dlls([r"@PROGRAMFILESX86@\Microsoft\Edge", r"@PROGRAMFILES@\Microsoft\Edge"])
