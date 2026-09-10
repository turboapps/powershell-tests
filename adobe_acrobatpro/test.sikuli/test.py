# Import the package "util" which contains common operations.
# More information: https://sikulix-2014.readthedocs.io/en/latest/scripting.html#importing-other-sikuli-scripts-reuse-code-and-images.
script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path) # This is needed to include screenshots from "util".

# Set the default waiting time.
setAutoWaitTimeout(30)

# Operations before running individual test.
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# The location to save a file in the test.
save_location = os.path.join(util.desktop, "Special_Offers_Deck.pdf")

# Acrobat 2026.001.21771 puts a "Set up Acrobat" onboarding modal over the first
# document view. It is never shown on the Home screen, so nothing before the
# conversion sees it, and it breaks the page check two ways at once: the modal
# dims the page behind it to about 9% brightness (the point-2-point logo region
# reads 0..28 where the reference reads 31..255) and its top edge cuts off the
# bottom 21% of the logo. point-2-point.png scores 0.34 against SikuliX' 0.7
# threshold, so the wait timed out in every App Tests run since 2026-09-01 --
# 34295135821 (xvm 26.9.26), 34295107851 (xvm 26.9.29) and the dedicated
# 34366434740 failed there pixel for pixel the same.
#
# Not a slow VM: the conversion had finished in each of them, the PDF is open
# and rendered in the failure frame. The modal has to be cleared, so no longer
# wait could have helped.
#
# get-started.png is the modal's heading and matches it at 0.9998, so finding it
# was never the problem -- dismissing it is. The three ESC presses this test
# already had were never reached (it died at the conversion check every time),
# so ESC has never been shown to close this modal. Click its X instead, 391 px
# right and 33 px above the centre of the heading match, and confirm the modal
# is gone; keep ESC only as the fallback.
def dismiss_setup_acrobat(timeout=1):
    m = exists("get-started.png", timeout)
    if not m:
        return False
    click(m.getTarget().offset(391, -33))
    for _ in range(10):
        wait(1)
        if not exists("get-started.png", 0.5):
            return True
    # The X was missed - the modal moved, or the click landed on the dimmed
    # page instead. Try the keyboard before giving up on it.
    type(Key.ESC)
    wait(2)
    if exists("get-started.png", 0.5):
        Debug.user("dismiss_setup_acrobat: modal still on screen after X and ESC")
    return True

# Wait for the converted page, clearing the onboarding modal whenever it turns
# up. The modal appears with the document view, which lands somewhere inside the
# conversion wait, so poll for both rather than dismissing once up front. The
# last attempt falls through to a plain wait() so a real failure still raises the
# usual FindFailed on point-2-point.png and leaves the standard FAILED step frame
# to investigate from.
def wait_page_rendered(attempts=12, poll=10):
    for _ in range(attempts):
        dismiss_setup_acrobat()
        if exists("point-2-point.png", poll):
            return
    wait("point-2-point.png", 5)


# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test turbo run
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
paste('turbo run acrobatpro --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test' + util.read_extra())
wait(2)
type(Key.ENTER)
if exists("adobe_login_signout_others.png",60):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("adobe_login_team.png",10):
    click(Pattern("adobe_login_continue.png").similar(0.80))
# Every Acrobat launch in this test is a container cold start, and the budgets
# these waits carried were all shorter than one. Validation run 34412874934 gave
# up on the Start-menu launch below after 60 s and its FAILED frame already shows
# the window: pdf_window.png scores 0.3542 when the wait starts and 0.9493 the
# moment it expires, so the window arrived just past the deadline. The reopen at
# the end of the test is the same story from run 34412866275 - a bare desktop
# 33 s after the relaunch, with the container still coming back up. These three
# waits are the same event ("Acrobat's window is up after a launch"), so give
# them one budget generous enough for a cold start.
wait("pdf_window.png",120)
run("turbo stop test")
closeApp("Command Prompt")

# Launch the app by Start menu shortcut.
run("explorer " + os.path.join(util.start_menu, "Adobe Acrobat Pro.lnk"))

# Basic operations.
click("pdf_window.png",120)
wait(5)
type(" ", Key.ALT)   # open system menu
wait(2)
type("x")            # maximize
wait(3)
wait("see-all-tools.png")
click("see-all-tools.png")
click("create-a-pdf.png")
wait("create-pdf-doc-icon.png")
click("create-pdf-doc-icon.png")
wait("create_file_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "get-started-acrobat-dc", "Special_Offers_Deck.pptx"))
wait(2)
type(Key.ENTER)
wait(5)
wait("create-button.png",120)
click("create-button.png")
wait_page_rendered()
type("s", Key.CTRL + Key.SHIFT)
wait("save_file_location.png")
paste(save_location)
wait(2)
type(Key.ENTER)
wait(5)
type("p", Key.CTRL)
wait("blue-print-button.png")
type(Key.ESC)
wait(3)
type(Key.F4, Key.ALT)

run("explorer " + save_location)
wait("default_dialog.png")
click("default_acrobat_pro.png")
click("default_always.png")
wait_page_rendered()
type(Key.F4, Key.ALT)
wait(3)

run("explorer " + save_location)
wait_page_rendered()

# Check the "help" of the app.
type(Key.F1)
wait("help_url.png")
util.close_app("Edge")
type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates after closing the app.
util.check_running()