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
# password-box.png is the "Password" label above a focused, blue-outlined box.
# The empty "Bluebeam ID" box of the *email* step looks near enough to that to
# score 0.704, which clears SikuliX's 0.7 default by 0.004 - so the click lands
# on the ID field and the password is typed into it in the clear. Measured with
# OpenCV TM_CCOEFF_NORMED: the ID field peaks at 0.704, a real password box at
# 0.949-0.985. 0.85 sits clear of both.
password_box_image = Pattern("password-box.png").similar(0.85)

def submit_email():
    click(email_box)
    type(username)
    type(Key.ENTER)

# Revu's splash panel can still be on top of the sign-in card when the click
# fires - it covers the whole field area - so the username lands on the splash
# instead of the field and the card never leaves the email step (run
# 34539429949). wait_first_run only proves the card is *visible*, and the
# wait(15) above is a guess, so check the outcome instead: getting from the
# email step to the password step is a full web-view reload (the card goes
# blank, "Loading... signin.bluebeam.com", re-renders the *email* step, then
# swaps in the password fields) and took ~26 s on 2026-09-10, so give the first
# attempt a generous look before deciding it never landed.
# PROBE: simulate the first click+type being swallowed by the Revu splash.
# submit_email()
if not exists(password_box_image, 60):
    # Still on the email step: the splash is long gone by now, so type into the
    # re-rendered card.
    submit_email()
wait(password_box_image, 120)
# The card keeps rendering after the password box first appears - the "Select
# Region" dropdown at its top lands late and pushes the fields down - so a click
# placed from the first sighting can miss. Let it settle and locate the box
# again at its final position. This used to fall back to a bare Tab when the
# re-location failed; that is how the password reaches an unknown field, so
# stop instead - nothing below this line is meaningful without a password box.
wait(3)
password_box = exists(password_box_image, 60)
if not password_box:
    raise FindFailed("password box vanished after the sign-in card settled")
click(password_box)
type(password)
type(Key.ENTER)
# The sign-in window closes once the credentials are accepted. Assert that here:
# without it a sign-in that never happened surfaces as a bogus help-window
# FindFailed ten lines below, pointing the investigation at the wrong step
# (run 34423171312). email-label.png is the card's "Bluebeam ID / (Your Email
# Address)" heading, present on both of its steps and nowhere else.
if not waitVanish("email-label.png", 120):
    raise FindFailed("sign-in did not complete: the Bluebeam sign-in window is still open")
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
# pdf-loaded.png is the "Name: <file>  Pages: 7" properties bar above the document:
# it does not depend on the zoom level Revu picks for the page (the drawing content
# rendered at a different scale in 21.11 than the previous capture).
wait("pdf-loaded.png")
closeApp("Revu")
wait(60)

# Check if the session terminates.
util.check_running()
