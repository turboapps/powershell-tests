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

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait("pdf_example.png",90)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Adobe Acrobat.lnk"))
wait("pdf_example.png",90)

# Basic operations.
type("o", Key.CTRL)
wait("open-file.png",15)
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
dismiss_ai_assistant()
type("s", Key.CTRL + Key.SHIFT)
if exists("cannot-save-ok.png",10):
    click("cannot-save-ok.png")
wait(Pattern("choose_diff_folder.png").similar(0.50))
click(Pattern("choose_diff_folder.png").similar(0.50))
wait("save_location.png")
wait(3)
paste(save_location)
type(Key.ENTER)
dismiss_ai_assistant()
type("p", Key.CTRL)
wait("print_window.png",60)
type(Key.ESC)
type(Key.F4, Key.ALT)
wait(15)
run("explorer " + util.desktop)
rightClick("test-pdf-file.png")
click("open-with.png")
click("choose-another-app.png")
click("open-with-adobe.png")
click("always.png")
wait("reader_opened.png")
type(Key.F4, Key.ALT)
wait(15)
run("explorer " + save_location)
wait("reader_opened.png",90)

# Check "help". Close the AI Assistant panel first so F1 reaches the app.
# Depending on whether GenAI is active, F1 either opens the help page in the
# system browser or submits a help query to the in-app AI Assistant.
# Accept both outcomes.
dismiss_ai_assistant()
type(Key.F1)
help_result = None
for _ in range(30):
    if exists(Pattern("reader_help_url.png"), 1):
        help_result = "browser"
        break
    if find_ai_panel(1):
        help_result = "assistant"
        break
assert help_result is not None, "F1 opened neither browser help nor AI Assistant"
if help_result == "browser":
    if App("Edge").isRunning(10):
        closeApp("Edge")
else:
    dismiss_ai_assistant()

# Test Adobe Login.
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
wait("account_icon.png",60)

# Quit the application.
type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates.
util.check_running()