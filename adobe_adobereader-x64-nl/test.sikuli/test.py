# The tests for adobe/adobereader and adobe/adobereader-x64 are almost the same except for the shortcut path.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

save_location = os.path.join(util.desktop, "test.pdf")

setAutoWaitTimeout(30)
util.pre_test()

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
type("s", Key.CTRL + Key.SHIFT)
if exists("cannot-save-ok.png",10):
    click("cannot-save-ok.png")
wait(Pattern("choose_diff_folder.png").similar(0.50))
click(Pattern("choose_diff_folder.png").similar(0.50))
wait("save_location.png")
wait(3)
paste(save_location)
type(Key.ENTER)
type("p", Key.CTRL)
wait("print_window.png")
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

# Check "help".
type(Key.F1)
wait("reader_help_url.png")
closeApp("Edge")

# Test Adobe Login.
click("sign_in_button.png")
wait(Pattern("login-email.png").similar(0.90),10)
click(Pattern("login-email.png").similar(0.90))
wait(3)
type(username)
wait(3)
type(Key.ENTER)
wait(Pattern("login-email.png").similar(0.90),15)
wait(3)
click(Pattern("login-email.png").similar(0.90))
wait(3)
type(password)
wait(3)
type(Key.ENTER)
wait("account_icon.png")

# Quit the application.
type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates.
util.check_running()