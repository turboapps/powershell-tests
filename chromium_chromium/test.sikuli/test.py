# The tests for google/chrome and google/chrome-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

save_location = os.path.join(util.desktop, "print.pdf")

# Test of `turbo run`.
wait("chrome_window.png",120)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Chromium.lnk"))
wait("chrome_window.png",120)

# Activate and maximize the app window.
app_window = App().focus("Chromium")
if app_window.isValid():
    type(Key.UP, Key.WIN)

# Basic operations.
type("l", Key.CTRL)
type("https://google.com/" + Key.ENTER)
wait(Pattern("webpage.png").similar(0.60))
wait(3)
type("s", Key.CTRL)
wait("save_type.png")
type(os.path.join(util.desktop, "name with space"))
click("save_type.png")
click("save_type_correct.png")
type(Key.ENTER)
assert(util.file_exists(os.path.join(util.desktop, "name with space.html"), 10))
type(Key.ESC)
type("l", Key.CTRL)
type("chrome://settings/" + Key.ENTER)
wait("settings_page.png")

# Check "help".
type(Key.F1)
wait("help_page.png")
type(Key.F4, Key.ALT)

# Set default browser.
type("i", Key.WIN)
wait("windows_setting_window.png")
type("Default apps")
type(Key.ENTER)
click("windows_setting_default.png")
wait(2)
click("windows_setting_default_browser_chrome.png")
click("set-default.png")
wait(5)
type(Key.F4, Key.ALT)
run("explorer " + os.path.join(util.desktop, "name with space.html"))
wait(Pattern("webpage.png").similar(0.60))
type(Key.F4, Key.ALT)
run('explorer "https://google.com/"')
click(Pattern("webpage.png").similar(0.60)) # To gain focus.
wait(2)
wait(Pattern("google-search2.png").similar(0.60))
wait(5)
type("p", Key.CTRL)
wait("print_window.png")
click(Pattern("print_print.png").targetOffset(-28,8))
wait("print_location.png")
type(save_location + Key.ENTER)
assert(util.file_exists(save_location, 5))

type(Key.ESC)
type(Key.F4, Key.ALT)
wait(5)

# Check if the session terminates.
util.check_running()