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

# The sign-in card is a web view that reloads whenever it likes: it goes blank
# ("Loading... signin.bluebeam.com"), comes back at the *email* step, and only
# then swaps in the password fields. The shape this replaces assumed that
# happened at most once, and only before the password box was first seen -
# submit, one look, one retry if that look failed, then a 120 s wait. Both
# assumptions cost a run in this PR's round-4 validation:
#
#   * 35794708819, and 35788530266 before it - the single look FOUND the
#     password box, so the retry was skipped; the card then reloaded back to the
#     email step and the 120 s wait never saw the box again.
#     FindFailed(password-box.png ... seen at (787, 596) with 0.98), where
#     "seen at" is SikuliX's lastSeen hint and not a current score.
#   * 35794698469 - the retry did fire, but by then a reload had moved the card
#     ON, so the blind click had no email-label.png to find:
#     FindFailed(email-label.png ... seen at (798, 367) with 0.88).
#
# So stop counting reloads. Look at which step the card is showing, do the thing
# that moves that step forward, and finish on the card closing - the only real
# evidence the sign-in took. A reload at any point just puts the loop back at
# the email step, which it already knows how to handle.
#
# Every click goes to the Match that was just found, never to a freshly built
# Pattern: clicking a Pattern searches the screen a second time, which is
# exactly how the 35794698469 FindFailed happened.
def sign_in(timeout):
    end = time.time() + timeout
    while time.time() < end:
        box = exists(password_box_image, 0)
        if box:
            # The card keeps rendering after the password box first appears -
            # the "Select Region" dropdown at its top lands late and pushes the
            # fields down - so let it settle and re-locate before clicking. If
            # it has gone by then the view reloaded under us, and going round
            # again is the one safe move: typing the password at a remembered
            # position is how it ends up in the Bluebeam ID field in the clear.
            wait(3)
            box = exists(password_box_image, 0)
            if not box:
                continue
            click(box)
            type(password)
            type(Key.ENTER)
            # The window closes once the credentials are accepted. If it is
            # still up, the card reloaded rather than signed in, and the loop
            # starts over from whichever step it came back at. email-label.png
            # is the card's "Bluebeam ID / (Your Email Address)" heading,
            # present on both of its steps and nowhere else.
            if waitVanish("email-label.png", 60):
                # The heading also goes away for a few seconds every time the
                # view reloads, so a vanish on its own is not proof that the
                # card closed. Settle and make sure neither step has come back
                # before calling the sign-in done.
                wait(5)
                if not exists("email-label.png", 0) and not exists(password_box_image, 0):
                    return True
            continue
        label = exists(email_box, 0)
        if label:
            click(label)
            type(username)
            type(Key.ENTER)
            # Getting from the email step to the password step is a full
            # web-view reload and took ~26 s on 2026-09-10, so give it a
            # generous look before concluding the submit did not land. It may
            # not have: Revu's splash panel can still cover the whole field area
            # when the click fires, putting the username on the splash instead
            # of in the field (run 34539429949).
            exists(password_box_image, 60)
            continue
        # Neither step is on screen: the view is mid-reload. Let it land.
        wait(2)
    return False


# password_box_image is matched at similar(0.85) - see above - and that is what
# keeps the password out of the Bluebeam ID field on the email step.
if not sign_in(360):
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


# "Always" both registers Revu as the .pdf handler and opens the file in it.
# What Revu puts on screen while that happens is NOT a fixed sequence, and
# waiting for one fixed step of it deadlocks whenever that is the step which
# does not come:
#
#   * default-pdf-ok.png - "Please confirm Revu as the default PDF viewer",
#     followed by the Windows Default apps page. Revu only raises it when it
#     finds it is not already the registered .pdf handler, which is exactly
#     what the "Always" click just made it, so whether it appears at all is a
#     race with the shell committing the association. It did NOT appear in
#     runs 35654098667 and 35678863980 - its best OpenCV TM_CCOEFF_NORMED
#     score over both 120 s waits was 0.32, i.e. absent rather than a near
#     miss - and the old wait("default-pdf-ok.png",120) on the line below was
#     where both runs died, together with 35168163987 before them.
#   * gfx-warning.png - "Hardware rendering has been disabled due to an issue
#     with the graphics driver". Up at the timeout in 35678863980 (0.989) and
#     never shown at all in 35654098667.
#   * "The file you are opening contains Layers. Would you like to open the
#     Layers Tab?" - a page banner, not a dialog. It blocks nothing.
#
# In both of those runs the document itself was open and rendered the whole
# time (pdf-loaded.png scores 0.944 on both FAILED frames): the test was
# blocked on an optional prompt while what it actually asserts had already
# happened. So dismiss whichever prompts are really up, in whatever order they
# come, and finish on the document.
# The prompt, with the click placed on its "Do not show this message again"
# checkbox by offset.
default_pdf_prompt = Pattern("default-pdf-ok.png").targetOffset(-180, 36)


def dismiss_default_viewer_prompt():
    """Revu's "confirm Revu as the default PDF viewer" prompt, if it is up.

    Ticks "Do not show this message again" (the targetOffset), presses the
    default OK button, and closes the Windows Default apps page that OK opens.

    The look and the click are one match, not two searches: clicking a freshly
    built Pattern searches the screen again, and run 35791961407 died there with
    FindFailed("default-pdf-ok.png ... seen at (751, 418) with 0.92") when the
    prompt closed in between. exists() on the offset Pattern returns a Match
    whose target already carries the offset, so click(prompt) needs no research.
    """
    prompt = exists(default_pdf_prompt, 0)
    if not prompt:
        return False
    click(prompt)
    type(Key.ENTER)
    # OK sends the shell to Settings > Default apps. Close that only once it is
    # really there: the Alt+F4 used to be unconditional, so on any run where
    # the page did not open it would have landed on Revu instead.
    if exists("default-apps.png", 30):
        wait(5)
        type(Key.F4, Key.ALT)
        waitVanish("default-apps.png", 30)
    return True


def dismiss_gfx_warning():
    """Revu's hardware-rendering warning, if it is up."""
    warning = exists("gfx-warning.png", 0)
    if not warning:
        return False
    click(warning)
    return True


def dismiss_open_prompts():
    """Clear whatever Revu is showing over the document. Order is not free:
    gfx-warning.png is a bare 50x22 "OK" button and matches the OK button of
    the default-pdf-ok dialog at 0.837, well over SikuliX's 0.7 threshold, so
    the large distinctive dialog has to be tested first."""
    return dismiss_default_viewer_prompt() or dismiss_gfx_warning()


# pdf-loaded.png is the "Name: <file>  Pages: 7" properties bar above the
# document: it does not depend on the zoom level Revu picks for the page (the
# drawing content rendered at a different scale in 21.11 than the previous
# capture).
pdf_loaded = None
deadline = time.time() + 180
while time.time() < deadline and not pdf_loaded:
    dismiss_open_prompts()
    # PROBE ONLY: an unmatchable magenta block in place of the real
    # document check, so the loop can never be satisfied. A run on this
    # branch must die at the deadline with "the sample PDF did not open in
    # Revu within 180 seconds"; if it passes, the loop is vacuous.
    pdf_loaded = exists("probe-never.png", 5)
if not pdf_loaded:
    raise FindFailed("the sample PDF did not open in Revu within 180 seconds")
# A prompt that arrived with or just after the document would otherwise still
# be modal when the app is closed below.
dismiss_open_prompts()


# The Open-with launch does not reuse the container the test has been working
# in: Windows runs Revu from shortcuts\Revu\DEFAULT.txt, which is a session of
# its own - `revu` in `turbo sessions -l`, next to the harness's `test`. So this
# close has to actually land, and closeApp() is fire-and-forget: it reports that
# it asked, not that Revu went away.
#
# It loses to a late prompt. Run 35776214358 had the document up at 13:51, ran
# closeApp, and at 13:54 still showed Revu with the Windows Default apps page
# covering the exact rect the default-viewer prompt renders in: the prompt this
# test used to block on had simply arrived minutes after the document instead of
# never, and a Revu with a modal up does not act on a close. check_running then
# spent its whole 60 s budget on a `revu` session that was never going to end
# and failed the run there, pointing at container teardown rather than at the
# close that never happened.
#
# The same loop covers a second Revu window surviving from the first launch:
# the two Alt+F4s at lines 46-48 are equally fire-and-forget, and when they do
# not finish before the shortcut relaunch the test ends up with two Revu
# windows and two sessions (that leftover is also why the default-viewer prompt
# goes missing in the first place - an associated launch handed to an already
# running Revu never runs the startup check that raises it).
def session_running():
    return "Running" in run("turbo sessions -l")


def close_revu():
    """Ask Revu to close, and treat "there is no Revu to close" as success.

    SikuliX's closeApp() raises java.lang.IndexOutOfBoundsException (Index: 0,
    Size: 0) when the named app has no window left. Run 35790322362 hit that on
    the very first call, because Revu had already exited on its own - the state
    this whole block exists to reach, not a failure. The session poll is the
    oracle here, not closeApp's temper.
    """
    try:
        closeApp("Revu")
    except:
        Debug.user("close_revu: no Revu window to close (%s)" % sys.exc_info()[1])


close_revu()
deadline = time.time() + 60
while time.time() < deadline:
    if not session_running():
        break
    # Something on screen is still holding a Revu open. Clear it and ask again.
    settings = exists("default-apps.png", 0)
    if settings:
        # Raise the Settings window first: an Alt+F4 sent while Revu has the
        # foreground would close the document instead and prove nothing.
        click(settings)
        type(Key.F4, Key.ALT)
    dismiss_open_prompts()
    close_revu()
    wait(5)

# Past this point nothing visible is left to clear, and a close that has nothing
# to address is not the same as a session that has ended. Run 35791920268 sat
# here with Revu gone from both the screen and the taskbar while its `revu`
# session stayed Running for the full 180 s that followed - a process tree with
# no window, which closeApp cannot reach and no amount of waiting fixes.
#
# end_session is what !include already offers for that: a last grace for the app
# to go on its own, then stop the session by id and assert the container tears
# down - which is Turbo's job rather than Revu's - instead of failing the run on
# the app's own habits. On a healthy run it returns at the first poll and this
# costs nothing. paintdotnet and azuredatastudio end the same way.
util.end_session()
