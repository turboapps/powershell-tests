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

# The sign-in window is a web page whose email field is focused automatically
# while the window is active, so the field itself renders with or without a
# focus ring depending on timing. Anchor on the "Bluebeam ID / (Your Email
# Address)" labels above the field, which never change, and click into the
# field by offset.
email_box = Pattern("email-label.png").targetOffset(85, 46)

# Wait for Revu's first-run UI and accept the terms dialog when it is shown.
# Up to Revu 21.10 the terms dialog ("I Accept") preceded the sign-in window on
# every first launch. Revu 21.11 (2026-09-01) redesigned the first-time user
# experience and opens the sign-in window directly, so the terms dialog is now
# optional: the app counts as up once either the terms dialog or the sign-in
# window's email box is visible, and the test only clicks "I Accept" if the
# terms dialog did appear.
def wait_first_run(timeout):
    end = time.time() + timeout
    while time.time() < end:
        if exists("agreement.png", 1):
            wait(5)
            click("agreement.png")
            type(Key.ENTER)
            wait("email-label.png", 60)
            return
        if exists("email-label.png", 1):
            return
    raise FindFailed("neither agreement.png nor email-label.png appeared within %d seconds" % timeout)

# Test of `turbo run`.
wait_first_run(120)
wait(10)
type(Key.F4, Key.ALT)
wait(5)
type(Key.F4, Key.ALT)
wait(10)

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.desktop, "Bluebeam Revu"))
wait_first_run(120)
wait(15)
click(email_box)
type(username)
type(Key.ENTER)
wait("password-box.png")
click("password-box.png")
type(password)
type(Key.ENTER)
wait(5)
# Check "help".
type(Key.F1)
wait("help-window.png")
type(Key.F4, Key.ALT)

# Launch sample pdf.
run("explorer " + os.path.join(script_path, os.pardir, "resources"))
wait(5)
rightClick("sample-pdf-file.png")
click("open-with-menu.png")
click("choose-another-app.png")
wait("open-with.png")
click("open-with.png")
wait(3)
click("always.png")
wait("default-pdf-ok.png",120)
click(Pattern("default-pdf-ok.png").targetOffset(-180,36))
type(Key.ENTER)
wait("default-apps.png")
wait(5)
type(Key.F4, Key.ALT)
wait("gfx-warning.png",10)
click("gfx-warning.png")
wait("pdf-loaded.png")
closeApp("Revu")
wait(60)

# Check if the session terminates.
util.check_running()
