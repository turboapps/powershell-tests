# The tests for adobe/adobereader and adobe/adobereader-x64 are almost the same except for the shortcut path.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import time
reload(util)
addImagePath(include_path)

save_location = os.path.join(util.desktop, "test.pdf")
# Remove a leftover from a previous run: an existing file triggers an
# overwrite-confirmation in the Save As dialog that the script does not handle.
if os.path.exists(save_location):
    os.remove(save_location)

setAutoWaitTimeout(30)
util.pre_test()

# Reader 26.001+ opens an AI panel over documents at unpredictable times; its
# prompt box swallows keystrokes (save/print/help shortcuts). The panel header
# reads "Ask AI Assistant" at first and flips to "Generative summary" once
# Reader starts summarizing the open file, sometimes within a second of
# appearing. Both headers share the close-button geometry (148x24 captures,
# close button 64 px left of center), so one offset serves both.
# ai_summary_close.png is only captured for some locales; missing captures
# are skipped so the helper degrades to the assistant-header check.
AI_PANEL_HEADERS = [img for img in ("ai_assistant_close.png", "ai_summary_close.png")
                    if os.path.exists(os.path.join(script_path, img))]

def find_ai_panel(timeout):
    for img in AI_PANEL_HEADERS:
        m = exists(img, timeout)
        if m:
            return m
    return None

# Close the AI panel whenever it is present before keyboard-driven steps.
# Click the match that was actually seen instead of re-searching by image: a
# re-search races the header flip and throws FindFailed on a panel that is
# still open.
def dismiss_ai_assistant():
    m = find_ai_panel(3)
    if not m:
        return
    click(m.getTarget().offset(-64, 0))
    for _ in range(10):
        wait(1)
        if not find_ai_panel(0.5):
            break
    wait(1)

# Reader (free) shows an "Unlock premium tools" upsell modal at random
# moments; it is web content, so its ADOBE ACROBAT header is the same in every
# locale. Close it via its window X (fixed offset from the header) when seen.
def dismiss_upsell():
    m = exists("upsell_acrobat.png", 1)
    if m:
        click(m.getTarget().offset(722, -69))
        wait(2)

# Keyboard shortcuts only reach Reader while its main window is active; other
# top-level windows (sign-in host, Explorer, coach marks) can take the focus
# between steps, and Reader hides its floating tool strip when that happens.
# Click an empty stretch of the title bar (right of the Create button, left of
# the help icon in every locale) to make the main window active again.
def focus_reader():
    bar = exists("reader_opened.png", 5)
    if bar:
        click(bar.getTarget().offset(500, 0))
        wait(1)

# Reader's toolbar is not visible while another window covers it, and then
# focus_reader() cannot click anything: F1 went to that window instead and
# Edge answered it with its own help page. Close whatever is on top until
# Reader's toolbar is reachable again.
def ensure_reader_front(attempts=3):
    for _ in range(attempts):
        focus_reader()
        if exists("reader_opened.png", 2):
            return True
        type(Key.F4, Key.ALT)
        wait(2)
    return False

# The 32-bit Reader offers an upgrade to the 64-bit build in a modal that can
# appear minutes after a document was opened, not only right after launch.
# The two buttons are right-aligned at fixed positions in every locale, so the
# capture is the boundary between the outlined "remind me later" button and
# the blue "yes" button; "remind me later" is 74 px to the left of it.
def dismiss_upgrade_prompt(timeout=1):
    m = exists("upgrade-to-64.png", timeout)
    if m:
        click(m.getTarget().offset(-74, 0))
        wait(2)

# Reader's window can take a long time to come up when the shell association
# starts it cold, and modals (the 64-bit upgrade prompt, the premium upsell)
# land on top of it while it does. Keep clearing them while waiting instead of
# waiting once and failing on whatever happened to be in the way.
def wait_reader_window(timeout=120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if exists("reader_opened.png", 3):
            return True
        dismiss_upgrade_prompt()
        dismiss_upsell()
    return False

# The help page opens in Edge at a localized URL (helpx.adobe.com/<lang>/...),
# so the browser is recognised by the address-bar prefix that every locale
# shares. SikuliX's App("Edge") is not usable for this: matched by process
# name it also hits the msedgewebview2 runtime behind Reader's sign-in and AI
# panes (closing that killed the sign-in dialog), and App("Microsoft Edge")
# did not resolve the browser window at all. Closing goes through the window
# itself: click the address bar to focus Edge, then Alt+F4.
def help_browser():
    return exists("help_url_prefix.png", 1)

def close_help_browser():
    bar = exists("help_url_prefix.png", 10)
    if not bar:
        return
    click(bar)
    wait(1)
    type(Key.F4, Key.ALT)
    wait(2)
    if exists("help_url_prefix.png", 3):
        type("w", Key.CTRL + Key.SHIFT)
        wait(2)

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait("pdf_example.png",90)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Acrobat Reader.lnk"))
wait("pdf_example.png",90)

# Basic operations.
type("o", Key.CTRL)
wait("open-file.png",60)
click("open-file.png")
paste(os.path.join(script_path, os.pardir, "resources", "homeacrordrunified18_2025.pdf"))
wait(2)
type(Key.ENTER)
assert wait_reader_window(), "Reader did not open the document"
wait(3)
dismiss_ai_assistant()
doubleClick("welcome-orig.png")
wait(2)
click("highlight.png")
wait("welcome_highlighted.png")
wait(3)
# Fill & Sign: open the tool from the strip, then its "add a signature" dialog.
# Both clicks land where they should and the dialog still does not always come
# up inside the 30 s default - two CI runs ended with the window dimmed behind a
# modal that never rendered, and the tool strip gone. Give the dialog longer and
# start the pair of clicks over if nothing arrives, clearing whatever is on top
# first (the upsell and the AI rail both take clicks meant for the strip).
sign_dialog = None
for attempt in range(3):
    dismiss_upsell()
    dismiss_ai_assistant()
    if attempt:
        # Put the window back the way the first attempt found it. The first
        # click hides the tool strip behind whatever it opened, and without
        # this the retry finds no toolbar.png, clicks nothing and is a no-op -
        # which is exactly what x64-fr did before this.
        type(Key.ESC)
        wait(1)
        ensure_reader_front()
        wait(2)
    strip = exists("toolbar.png", 20)
    if not strip:
        continue
    click(strip.getTarget().offset(0, 107))
    tool = exists("tool_sign.png", 15)
    if not tool:
        continue
    click(tool.getTarget().offset(1, -34))
    sign_dialog = exists("sign_window.png", 40)
    if sign_dialog:
        break
assert sign_dialog is not None, "Fill & Sign did not open its signature dialog"
type("turbo" + Key.ENTER)
wait(3)
click("sign_before.png")
type(Key.ESC)
wait("sign_after.png")
# Leave the Fill & Sign tool before using keyboard shortcuts: while it is the
# active tool (seen on x64 locales) Ctrl+Shift+S is swallowed and the Save As
# dialog never opens. Switching back to the Select tool restores them.
select_tool = exists("arrow_tool.png", 5)
if select_tool:
    click(select_tool)
    wait(1)
    # The Select button carries a flyout chevron (Select / Pan); the small
    # glyph match can land on it and open the menu, which would swallow the
    # next shortcut. Escape closes the flyout and is a no-op otherwise.
    type(Key.ESC)
    wait(1)
dismiss_ai_assistant()
# Reader's left rail - the "All tools" list, or the AI "Read" panel with its
# suggestion pills - can hold the keyboard focus, and then Ctrl+Shift+S goes to
# the rail instead of the document and the Save As sheet never opens. Two CI
# runs failed that way with the Read panel on screen. The rail's close button
# sits at a fixed offset from the toolbar anchor in every locale and in both
# builds, so look for it there (and only there, so the bare X cannot match
# something else) and close the rail when it is open.
def close_side_panel():
    bar = exists("reader_opened.png", 2)
    if not bar:
        return
    anchor = bar.getTarget()
    spot = Region(max(0, anchor.x + 150), max(0, anchor.y + 60), 70, 70)
    m = spot.exists("panel_close.png", 1)
    if m:
        click(m)
        wait(1)

# The blue "Choose a different folder" button now has a capture in its own
# language in every folder, so it is matched at the normal 0.70 rather than the
# 0.50 a foreign label needed - the AI rail's suggestion pills, which used to
# win that search at 0.517 and send a prompt to the AI Assistant instead of
# opening the file dialog, cannot reach it any more. The search stays confined
# to the document area as a second line of defence.
def reader_content_region():
    bar = exists("reader_opened.png", 3)
    if not bar:
        return SCREEN
    anchor = bar.getTarget()
    x = max(0, min(anchor.x + 250, SCREEN.getW() - 200))
    y = max(0, anchor.y - 40)
    return Region(x, y, min(1000, SCREEN.getW() - x), min(1000, SCREEN.getH() - y))

# Save As: Reader's own "Save as" sheet first, then "Choose a different
# folder" opens the system file dialog. A Reader upsell modal ("Unlock premium
# tools") can pop up at any point and swallow the sheet, so dismiss it and
# retry the whole sequence once before giving up.
save_dialog = None
for _ in range(3):
    dismiss_upsell()
    dismiss_upgrade_prompt()
    # The AI panel takes the keystroke as prompt text while it is open, so
    # it has to be cleared on every attempt, not only before the first one.
    dismiss_ai_assistant()
    close_side_panel()
    ensure_reader_front()
    type("s", Key.CTRL + Key.SHIFT)
    if exists("cannot-save-ok.png", 10):
        click("cannot-save-ok.png")
    sheet = reader_content_region().exists(
        Pattern("choose_diff_folder.png").similar(0.70), 40)
    if sheet:
        click(sheet)
        save_dialog = exists("save_location.png", 40)
        if save_dialog:
            break
    # Nothing came up. Escape closes a panel or flyout that took the shortcut
    # and is a no-op otherwise, so the next attempt starts from a clean window.
    type(Key.ESC)
    dismiss_upsell()
if not save_dialog:
    wait("save_location.png", 5)
wait(3)
paste(save_location)
type(Key.ENTER)
dismiss_upsell()
dismiss_upgrade_prompt()
dismiss_ai_assistant()
focus_reader()
type("p", Key.CTRL)
wait("print_window.png",60)
type(Key.ESC)
type(Key.F4, Key.ALT)
wait(15)
run("explorer " + util.desktop)
# The saved file shows Reader's icon once the app owns the .pdf association,
# but the stock Edge PDF icon when it does not yet (seen on x64 locales);
# accept either row rendering.
#
# The row must be located again right before it is right-clicked. The Explorer
# window is still settling into place when the first match comes back, and the
# harness writes its own <app>-test.log and <app>-executor.log onto the same
# Desktop while the test runs, so rows appear and the list shifts under a
# position captured a moment earlier - a stale match right-clicks a log file
# and the Open with flow then runs against the wrong file type. Wait until the
# same row matches twice in the same place before using it.
def find_pdf_row(timeout=45):
    deadline = time.time() + timeout
    previous = None
    while time.time() < deadline:
        # Score both renderings and take the better one rather than the first
        # that clears the threshold: whichever icon the row is actually showing
        # matches near 1.0, while the other one can still find a weak match
        # somewhere else in the list (a log file whose name also ends in
        # "test") and win purely by being checked first.
        candidates = [m for m in (exists("test-pdf-file.png", 1),
                                  exists("test-pdf-file-edge.png", 1)) if m]
        if candidates:
            row = candidates[0]
            for other in candidates[1:]:
                if other.getScore() > row.getScore():
                    row = other
            here = row.getTarget()
            if previous and abs(here.x - previous.x) < 3 and abs(here.y - previous.y) < 3:
                return row
            previous = here
        wait(1)
    return None

pdf_row = find_pdf_row()
assert pdf_row is not None, "test.pdf row not found on the Desktop"
rightClick(pdf_row)
click("open-with.png")
click("choose-another-app.png")
click("open-with-adobe.png")
click("always.png")
assert wait_reader_window(), "Reader did not open the file from the Desktop"
type(Key.F4, Key.ALT)
wait(15)
run("explorer " + save_location)
assert wait_reader_window(), "Reader did not reopen the saved file"

# Check "help". Close the AI Assistant panel first so F1 reaches the app.
# Depending on whether GenAI is active, F1 either opens the help page in the
# system browser or submits a help query to the in-app AI Assistant.
# Accept both outcomes.
dismiss_upsell()
dismiss_upgrade_prompt()
dismiss_ai_assistant()
ensure_reader_front()
type(Key.F1)
help_result = None
for attempt in range(30):
    if attempt in (10, 20):
        # Nothing showed up yet. Reader does not always act on F1 (a modal may
        # have taken the keystroke, or the window was still settling), so
        # clear what is on screen, refocus and send it again.
        dismiss_upsell()
        dismiss_upgrade_prompt()
        dismiss_ai_assistant()
        ensure_reader_front()
        type(Key.F1)
    if help_browser():
        help_result = "browser"
        break
    if find_ai_panel(1):
        help_result = "assistant"
        break
assert help_result is not None, "F1 opened neither browser help nor AI Assistant"
# F1 can produce both outcomes at once: the AI panel is already open (summary
# mode after reopening the file) and the help page still opens in Edge a few
# seconds later. Whichever was detected first, clear both before moving on;
# an Edge window left open would cover Reader's Sign in button.
wait(3)
dismiss_ai_assistant()
close_help_browser()

# Test Adobe Login.
#
# Adobe shows a "set up a passkey" interstitial after some - not all - of these
# sign-ins, and that is what the account_icon timeouts in CI were: the
# interstitial was still on screen and nothing was going to move it. It has to
# be dismissed to finish signing in, it can arrive well after the password is
# submitted, and the Skip button sits at a locale-dependent height, so the
# interstitial is polled for alongside the account icon (rather than looked for
# once, before it) and clicked by its own capture where one exists. The rest of
# the exchange re-locates every anchor right before using it, because the page
# keeps rendering while it is being clicked, and the whole thing is retried once
# if it does not finish.
PASSKEY_SKIP = "passkey_skip.png" if os.path.exists(
    os.path.join(script_path, "passkey_skip.png")) else None

# Reaching Skip without a capture of it. What changes between locales is the
# words on the buttons and how far down the card they sit; what does not change
# is the shape of the row - an outlined Skip pill, an 18 px gap, then the blue
# "Set up passkey" button. passkey_primary_left.png is that blue button's
# rounded left corner, cropped short of the first glyph, so it is geometry
# rather than text and matches in any language; Skip is 38 px to its left.
#
# The search has to be confined to the card, anchored on the wand: Reader's own
# blue pills match the same corner just as well (the Free trial button in the
# tools rail scores 0.994, Share in the toolbar 0.845), and they sit outside
# that region.
PASSKEY_PRIMARY = "passkey_primary_left.png"

def click_passkey_skip(anchor):
    """Click Skip using the blue primary button as the anchor. True if clicked."""
    left = max(0, anchor.x - 60)
    top = max(0, anchor.y - 20)
    card = Region(left, top,
                  min(700, SCREEN.getW() - left), min(720, SCREEN.getH() - top))
    m = card.exists(Pattern(PASSKEY_PRIMARY).similar(0.80), 1)
    if not m:
        return False
    click(m.getTarget().offset(-38, 0))
    return True

# Last-resort offsets from the wand, for a card whose primary button cannot be
# found either. They only ever step left and down - "Set up passkey" is
# immediately to the right of Skip, and clicking that would start creating a
# passkey instead.
PASSKEY_SKIP_OFFSETS = ((149, 354), (131, 400), (131, 446), (105, 400))

# login-password.png is the English capture in every folder but fr, and it
# scores only 0.77 against the localized page (measured on the Spanish one) -
# clearing the 0.70 default with little to spare, and dropping to 0.69 once the
# click has left a focus ring on the field. Everything here therefore matches it
# before clicking, never after.
LOGIN_EMAIL = Pattern("login-email.png").similar(0.70)

# The show/hide eye at the right end of the password box is the only reliable
# way to tell that page apart from the email page, and the only one that does
# not depend on the language: 1.000 on the English, Spanish and Dutch password
# pages, 0.544 on the email page. The label above the box is localized AND the
# capture of it matches an empty email box at 0.614, which is what sent a
# password into the email field on x64-es. The box centre is 178 px left of the
# eye.
LOGIN_PASSWORD_EYE = Pattern("login_password_eye.png").similar(0.90)

def password_page():
    return exists(LOGIN_PASSWORD_EYE, 0)

def find_password_box():
    """Where to click to put the caret in the password field, or None."""
    eye = password_page()
    return eye.getTarget().offset(-178, 0) if eye else None

# Anchors that only ever appear on the sign-in host. The email field is not one
# of them - it is an empty rounded box that Reader's own search field can match
# - so it counts only once the host has been asked for, which is the only way
# the English layout (no Adobe wordmark, no password box yet) can be seen at
# all.
def signin_anchored():
    return (exists("adobe_signin_logo.png", 0) or password_page()
            or exists("passkey_prompt.png", 0))

def signin_visible():
    return signin_anchored() or exists(LOGIN_EMAIL, 0)

# Bring the sign-in host up (or back): Reader reuses the existing window, on the
# page it was left on, when its Sign in button is clicked again. The host takes
# its time to render, so click once and then wait for it rather than clicking
# again every few seconds.
def open_signin(timeout=60):
    if signin_anchored():
        return True
    button = exists(Pattern("sign_in_button.png").similar(0.70), 5)
    if not button:
        return False
    click(button)
    deadline = time.time() + timeout
    while time.time() < deadline:
        if signin_visible():
            return True
        wait(2)
    return False

def enter_email():
    # Two layouts: a wide one with a marketing panel beside the form (the
    # English apps) and a compact one headed by the red Adobe wordmark (the
    # localized apps). login-email.png matches the field itself, the wordmark
    # only the compact layout - so wait for whichever shows up. The dialog
    # keeps rendering after the anchor first appears and shifts as it settles,
    # so let it settle and locate the anchor again before clicking.
    field = None
    logo = None
    for _ in range(30):
        field = exists(LOGIN_EMAIL, 1)
        if field:
            break
        logo = exists("adobe_signin_logo.png", 1)
        if logo:
            break
    wait(5)
    field = exists(LOGIN_EMAIL, 3)
    if field:
        click(field)
    else:
        logo = exists("adobe_signin_logo.png", 5) or logo
        if not logo:
            return False
        click(logo.getTarget().offset(159, 173))
    wait(2)
    type(username)
    wait(3)
    type(Key.ENTER)
    return True

def enter_password():
    # The page offers "Sign in with a code" (the primary button) or a
    # "Continue with password" field; use the password path. A click that
    # misses the field leaves the box empty, and Enter on an empty box does
    # nothing at all, so locate the field again once the page has settled.
    target = None
    for _ in range(20):
        target = find_password_box()
        if target:
            break
        wait(1)
    if not target:
        return False
    wait(2)
    target = find_password_box() or target   # the page shifts while it settles
    click(target)
    wait(2)
    # SikuliX logs every keystroke it sends, and <app>-test.log is uploaded as a
    # diagnostics artifact on every failed run of a public repository, so the
    # account password was going out in clear text. Turn the action log off
    # around the one line that carries it.
    Settings.ActionLogs = False
    type(password)
    Settings.ActionLogs = True
    wait(3)
    type(Key.ENTER)
    return True

# Wait for the account icon while clearing whatever Adobe puts in the way. The
# passkey interstitial is anchored on its locale-independent wand
# illustration; the Skip button below it is not (the localized body text wraps
# differently, moving the button row), so click the button itself where a
# capture of it exists and fall back to the offset elsewhere.
def wait_signed_in(timeout=240):
    deadline = time.time() + timeout
    tried = 0
    scrolled = 0
    while time.time() < deadline:
        if exists("account_icon.png", 2):
            return True
        # Look for the Skip button before the wand: once the card has been
        # scrolled the wand can be off the top while the buttons are finally in
        # view, and the button is the thing worth clicking either way.
        skip = exists(PASSKEY_SKIP, 1) if PASSKEY_SKIP else None
        if skip:
            click(skip)
            wait(3)
            continue
        passkey = exists("passkey_prompt.png", 1)
        if passkey:
            anchor = passkey.getTarget()
            if click_passkey_skip(anchor):
                wait(3)
                continue
            # Neither capture matched, so the button row is not on screen: the
            # 32-bit sign-in host is shorter than the card and cuts the row off
            # below the fold, where no offset can reach it either. Scroll the
            # card and look again; the blind offsets are only for a card whose
            # primary button still cannot be found after that.
            if scrolled < 4:
                wheel(anchor, WHEEL_DOWN, 5)
                scrolled += 1
                wait(2)
                continue
            if tried < len(PASSKEY_SKIP_OFFSETS):
                click(anchor.offset(*PASSKEY_SKIP_OFFSETS[tried]))
                tried += 1
                wait(3)
                continue
            # Nothing found the button. The password was already accepted at
            # this point, so close the interstitial and let the outer retry see
            # whether Reader came out of it signed in.
            type(Key.ESC)
            wait(3)
            continue
        if not signin_visible():
            # The host is gone and Reader is still signed out: nothing more is
            # going to happen on its own, so stop waiting and let the caller
            # start the exchange again.
            return False
        wait(2)
    # Signing in has been seen to take over 150 s on a loaded pool VM; give the
    # icon one last look before reporting failure.
    return exists("account_icon.png", 10) is not None

signed_in = False
for attempt in range(2):
    dismiss_upsell()
    dismiss_upgrade_prompt()
    dismiss_ai_assistant()
    if exists("account_icon.png", 1):
        signed_in = True
        break
    if not open_signin():
        continue
    if exists(LOGIN_PASSWORD_EYE, 2):
        submitted = enter_password()
    else:
        submitted = enter_email() and enter_password()
    if submitted and wait_signed_in():
        signed_in = True
        break
if not signed_in:
    signed_in = exists("account_icon.png", 30) is not None
assert signed_in, "Adobe sign-in did not complete: the account icon never appeared"

# Quit the application. After sign-in a hidden helper window (the sign-in
# host) can still own the keyboard focus, so Alt+F4 closes that instead of
# Reader and the session stays up. Focus the main window, then use the
# app-level Exit shortcut Ctrl+Q; fall back to Alt+F4 if the document window
# is still there.
wait(3)
focus_reader()
type("q", Key.CTRL)
wait(30)
if exists("reader_opened.png", 3):
    type(Key.F4, Key.ALT)
    wait(30)
# The session check that follows only allows 60 s for the session to go away,
# so do not start counting until the window has actually gone.
for _ in range(20):
    if not exists("reader_opened.png", 1):
        break
    wait(3)

# Check if the session terminates.
util.check_running()