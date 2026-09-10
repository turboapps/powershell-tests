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


# Alt+F4 closes Acrobat's window, but the container session outlives it: the
# session's root `turbo run` only reports "Application exited" seconds later, and
# the session is torn down at that point. Reopening the PDF inside that window is
# fatal - `turbo execute` finds the session still listed, logs
#   Existing session with policy: "Default"
#   Existing session with different args, switching to LaunchInSession
# and returns 0, but the Acrobat it just started dies with the session moments
# later. Run 34421003089 attached at 17:45:23 and the root app exited at 17:45:26,
# and the screen then stayed pixel-identical (mean frame diff 0.00) for the whole
# 120 s wait - no window, no error. Run 34421011469 did the same LaunchInSession
# but had 42 s before its root app exited, so it survived. It is a race with the
# teardown, not a slow launch, which is why widening the wait to 120 s in #195
# changed nothing.
#
# So let the session finish dying before relaunching; the reopen then starts a
# fresh container. Returns False rather than asserting - the page wait that
# follows stays the assertion, and a session that never clears should show up
# there with a screenshot rather than here.
def wait_session_gone(attempts=20, delay=3):
    for _ in range(attempts):
        if "Running" not in run("turbo sessions -l"):
            return True
        wait(delay)
    Debug.user("wait_session_gone: a session is still Running after %d s" % (attempts * delay))
    return False

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test turbo run
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
# Run 34420994008 lost this paste outright: the prompt is empty in the step frame
# before the paste and still empty before the Enter, and the console shows two
# bare prompts 120 s later - so the window had the keyboard (it took the Enter)
# but Ctrl+V never produced anything, and the text never arrived at all. Pressing
# Enter on the empty line then leaves the container unstarted and the test waits
# out the launch it never asked for.
#
# So check the command is on the prompt before submitting it, and re-send it if
# not. Esc clears cmd's input line first, so a retry - including one caused by
# this image going stale - can only ever leave a single copy of the command on
# the line. The wait for the app below stays the assertion.
turbo_run = ('turbo run acrobatpro --using=isolate-edge-wc,creativeclouddesktop'
             ' --offline --enable=disablefontpreload --name=test' + util.read_extra())
for attempt in range(3):
    type(Key.ESC)
    util.paste_text(turbo_run, 2)
    if exists("turbo-run-pasted.png", 2):
        break
    Debug.user("turbo run: the paste did not reach the prompt on attempt %d of 3" % (attempt + 1))
type(Key.ENTER)
if exists("adobe_login_signout_others.png",60):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("adobe_login_team.png",10):
    click(Pattern("adobe_login_continue.png").similar(0.80))
# The turbo run keeps this console in the foreground, and Acrobat does not
# reliably raise itself above it. pdf_window.png anchors on the window's top-left
# chrome at (6,4) 191x73, and in run 34529738531 the Command Prompt covered
# (52,52)-(1165,680) - so the bottom of the match region was behind the console
# and the wait timed out with Acrobat plainly up: the FAILED frame shows the
# command's full output ("Using VM 26.9.29.1055 ... Running new session
# test#f15a37e2") and the Acrobat window behind the console. Whether Acrobat wins
# the z-order race is chance, which is why this is not a budget - #197 already
# established that widening this wait changes nothing.
#
# So raise Acrobat before looking for it. focus() on a name that matches nothing
# is a no-op, so the worst case is the behaviour this replaces; the plain wait()
# below is still the assertion and still leaves the usual FAILED frame.
if not util.focus_and_wait("Acrobat", "pdf_window.png", attempts=6, poll=5):
    wait("pdf_window.png", 5)
run("turbo stop test")
closeApp("Command Prompt")

# Launch the app by Start menu shortcut.
run("explorer " + os.path.join(util.start_menu, "Adobe Acrobat Pro.lnk"))

# Basic operations.
# The window can arrive just past 60 s. Validation run 34412874934 gave up here
# and its FAILED frame already shows Acrobat: pdf_window.png scores 0.3542 when
# the wait starts and 0.9493 the moment it expires. Only this launch is widened -
# 120 s was tried at the first launch and at both reopens too and changed nothing
# there, because those failures are not slow launches (see runs 34420994008 and
# 34421003089).
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
wait_session_gone()

run("explorer " + save_location)
wait("default_dialog.png")
click("default_acrobat_pro.png")
click("default_always.png")
wait_page_rendered(3)
type(Key.F4, Key.ALT)
wait_session_gone()

run("explorer " + save_location)
wait_page_rendered(3)

# Check the "help" of the app.
type(Key.F1)
wait("help_url.png")
util.close_app("Edge")
type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates after closing the app.
util.check_running()