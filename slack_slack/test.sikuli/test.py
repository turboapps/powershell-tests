# The tests for google/chrome and google/chrome-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

save_location = os.path.join(util.desktop, "print.pdf")

# Test of `turbo run`.
wait("slack-sign-in.png")
run("turbo stop test")

# Launch Slack and login with email address
run("explorer " + os.path.join(util.desktop, "Slack.lnk"))
wait("slack-sign-in.png")
click("slack-sign-in.png")
util.close_firewall_alert_continue(wait_time = 30)

# Activate and maximize the app window.
app_window = App().focus("Edge")
if app_window.isValid():
    type(Key.UP, Key.WIN)
    
wait("email-prompt.png")
click("email-prompt.png")
type(username)
click("sign-in-with-email.png")
wait("one-time-code-box.png")

# Get the Slack one-time login code from Outlook
run('explorer "https://outlook.office.com/mail/"')
util.close_firewall_alert_continue(wait_time = 20)

# Activate and maximize the app window.
app_window = App().focus("Edge")
if app_window.isValid():
    type(Key.UP, Key.WIN)

wait("outlook-sign-in.png")
type(username)
type(Key.ENTER)
wait("outlook-password.png")
click(Pattern("outlook-password.png").targetOffset(-61,18))
type(password)
type(Key.ENTER)
click("stay-signed-in.png")
wait("slack-code-email.png")
click("slack-code-email.png")
wait("slack-code-subject.png")
dragDrop(Pattern("slack-code-subject.png").targetOffset(55,0), Pattern("slack-code-subject.png").targetOffset(135,0))

# Paste the one-time code into Slack login
type("c", Key.CTRL)
type(Key.F4, Key.ALT)
wait("one-time-code-box.png")
click("one-time-code-box.png")
type("v", Key.CTRL)
wait("always-allow.png")
click(Pattern("always-allow.png").targetOffset(-38,0))
click("open-slack.png")

# Test launching Slack help
wait("slack-menu.png")
wait(10)
type(Key.F1)
wait("slack-help.png")
type(Key.F4, Key.ALT)
wait(3)
type("q", Key.CTRL)

# Close the Edge browser
# Activate and maximize the app window.
app_window = App().focus("Edge")
if app_window.isValid():
    type(Key.UP, Key.WIN)
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()