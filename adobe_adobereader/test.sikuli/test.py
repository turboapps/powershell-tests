# The tests for adobe/adobereader and adobe/adobereader-x64 are almost the same except for the shortcut path.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
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
wait("reader_opened.png")
wait(3)
dismiss_ai_assistant()
doubleClick("welcome-orig.png")
wait(2)
click("highlight.png")
wait("welcome_highlighted.png")
wait(3)
click(Pattern("toolbar.png").targetOffset(0,107))
click(Pattern("tool_sign.png").targetOffset(1,-34))
wait("sign_window.png")
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
# Save As: Reader's own "Save as" sheet first, then "Choose a different
# folder" opens the system file dialog. A Reader upsell modal ("Unlock premium
# tools") can pop up at any point and swallow the sheet, so dismiss it and
# retry the whole sequence once before giving up.
save_dialog = None
for _ in range(2):
    dismiss_upsell()
    dismiss_upgrade_prompt()
    focus_reader()
    type("s", Key.CTRL + Key.SHIFT)
    if exists("cannot-save-ok.png", 10):
        click("cannot-save-ok.png")
    sheet = exists(Pattern("choose_diff_folder.png").similar(0.50), 20)
    if sheet:
        click(sheet)
        save_dialog = exists("save_location.png", 20)
        if save_dialog:
            break
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
pdf_row = exists("test-pdf-file.png", 15) or exists("test-pdf-file-edge.png", 15)
assert pdf_row is not None, "test.pdf row not found on the Desktop"
rightClick(pdf_row)
click("open-with.png")
click("choose-another-app.png")
click("open-with-adobe.png")
click("always.png")
wait("reader_opened.png")
dismiss_upgrade_prompt(30)
type(Key.F4, Key.ALT)
wait(15)
run("explorer " + save_location)
wait("reader_opened.png",90)
dismiss_upgrade_prompt(30)

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
    if attempt == 15:
        # Nothing showed up within 15 s: a modal (upgrade prompt, upsell) may
        # have taken the keystroke. Clear them, refocus and press F1 again.
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
dismiss_upsell()
dismiss_upgrade_prompt()
click("sign_in_button.png")
wait(Pattern("login-email.png").similar(0.90),10)
# The dialog keeps rendering after the field first appears: it shifts down and
# auto-focuses (focus ring breaks a 0.90 match). Let it settle, then click at
# relaxed similarity; if the focused field no longer matches, it already has
# focus, so typing works either way.
wait(3)
field = exists(Pattern("login-email.png").similar(0.70), 10)
if field:
    click(field)
    wait(2)
type(username)
wait(3)
type(Key.ENTER)
# The next page offers "Sign in with a code" (default) or a
# "Continue with password" field; use the password path.
wait("login-password.png",15)
click(Pattern("login-password.png").targetOffset(0,12))
wait(2)
type(password)
wait(3)
type(Key.ENTER)
# Adobe may follow a successful password with a "set up a passkey"
# interstitial. Its text is localized, but the wand illustration is not; the
# Skip button sits at a fixed offset below it. Skip it when it shows.
passkey = exists("passkey_prompt.png", 20)
if passkey:
    click(passkey.getTarget().offset(149, 354))
    wait(3)
wait("account_icon.png",60)

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

# Check if the session terminates.
util.check_running()