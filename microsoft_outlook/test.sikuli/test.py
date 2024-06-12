script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(40)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait("email-prompt.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.desktop, "Outlook (new).lnk"))
wait("email-prompt.png")
click("email-prompt.png")
type(username)
type(Key.ENTER)
wait("sign_in_password.png")
type(password)
type(Key.ENTER)
wait("sign_in_stay_signed_in.png")
click("sign_in_ok.png")
if exists("sign_in_went_wrong.png"):
    click("sign_in_continue.png")
else:
    wait("sign_in_all_set.png")
    click("sign_in_done.png")
click("not-interested.png")
wait("new-mail-button.png")
click("new-mail-button.png")
wait("email-to.png")
click("email-to.png")
type("sandy@gridturbo.onmicrosoft.com")
type(Key.TAB)
type(Key.TAB)
type("sikulix test email")
type(Key.TAB)
type("This email can be deleted.")
click("send-email-button.png")
wait(5)
click("calendar-button.png")
wait("today-icon.png")
click("print-button.png")
wait("blue-print-button.png")
click("blue-print-button.png")
wait("second-blue-print-button.png")
wait(5)
type(Key.ESC)
wait(5)
type(Key.ESC)
wait(5)
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()