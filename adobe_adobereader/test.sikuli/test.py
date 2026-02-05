# The tests for adobe/adobereader and adobe/adobereader-x64 are almost the same except for the shortcut path.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

# Log in for Adobe Creative Cloud for Adobe Reader.
def adobe_cc_login(username, password):
    wait("adobe_login.png", 90)
    wait(30)
    click("adobe_login.png")
    wait(3)
    paste(username)
    wait(3)
    type(Key.ENTER)
    wait("adobe_login_pass.png", 90)
    wait(3)
    click("adobe_login_pass.png")
    wait(3)
    paste(password)
    wait(3)
    type(Key.ENTER)
    if exists("adobe_login_signout_others.png", 15):
        click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
        click(Pattern("adobe_login_continue.png").similar(0.90))
    if exists("adobe_login_team.png",10):
        click(Pattern("adobe_login_continue.png").similar(0.90))

save_location = os.path.join(util.desktop, "test.pdf")

setAutoWaitTimeout(30)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait("reader_window.png",90)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Acrobat Reader.lnk"))
wait("reader_window.png",90)

# Basic operations.
doubleClick("pdf_example.png")
if exists("see_menu_options.png",10):
    click(Pattern("see_menu_options.png").targetOffset(-13,46))
wait("reader_opened.png")
wait(3)
doubleClick("welcome-orig.png")
rightClick("welcome_selected.png")
wait(3)
type("h")
wait("welcome_highlighted.png")
wait(3)
click(Pattern("toolbar.png").targetOffset(0,107))
click(Pattern("tool_sign.png").targetOffset(32,-36))
wait("sign_window.png")
type("turbo" + Key.ENTER)
wait(3)
click("sign_before.png")
type(Key.ESC)
wait("sign_after.png")
type("s", Key.CTRL + Key.SHIFT)
if exists("cannot-save-ok.png",10):
    click("cannot-save-ok.png")
wait("choose_diff_folder.png")
click("choose_diff_folder.png")
wait("save_location.png")
paste(save_location)
type(Key.ENTER)
type("p", Key.CTRL)
wait("print_window.png")
type(Key.ESC)
type(Key.F4, Key.ALT)
wait(15)
run("explorer " + save_location)
wait("default_dialog.png")
click("new_acrobat_reader.png")
click("default_always.png")
wait("reader_opened.png")
wait(10)
type(Key.F4, Key.ALT)
wait(15)
run("explorer " + save_location)
wait("reader_opened.png",90)

# Check "help".
type(Key.F1)
wait("reader_help_url.png")
closeApp("Edge")
wait("upgrade-prompt.png",20)
click("upgrade-prompt.png")

# Test Adobe Login.
click("sign_in_button.png")
wait(Pattern("login-email.png").similar(0.80),10)
click(Pattern("login-email.png").similar(0.80))
wait(3)
type(username)
wait(3)
type(Key.ENTER)
wait(Pattern("adobe_login_pass-1.png").similar(0.60),15)
wait(3)
click(Pattern("adobe_login_pass-1.png").similar(0.60))
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