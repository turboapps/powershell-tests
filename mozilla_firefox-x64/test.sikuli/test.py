# The tests for mozilla/firefox and mozilla/firefox-x64 are the same.

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
wait("firefox_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Firefox.lnk"))
wait("firefox_window.png")

# Basic operations.
type("https://turbo.net/" + Key.ENTER)
wait("turbo_webpage.png")
wait(3)
type("s", Key.CTRL)
wait("save.png")
type(os.path.join(util.desktop, "name with space"))
click("save_type.png")
click("save_type_correct.png")
type(Key.ENTER)
wait(60) # Wait for the file to be created.
assert(os.path.exists(os.path.join(util.desktop, "name with space.htm")))
click("menu.png")
click("menu_settings.png")
wait("settings_page.png")

# Check "help".
click("menu.png")
wait(2)
click("menu_help.png")
click("menu_item_get_help.png")
wait("help_page.png")
type("q", Key.CTRL + Key.SHIFT)

# Set default browser.
type("i", Key.WIN)
wait("windows_setting_window.png")
type("Default apps")
click("windows_setting_default.png")
click(Pattern("maximize_default_window.png").targetOffset(-2,-4))
click(Pattern("choose_browser.png").targetOffset(-58,18))
wait(2)
click(Pattern("windows_setting_default_firefox.png").similar(0.90))
if exists("windows_setting_default_anyway.png"):
    click("windows_setting_default_anyway.png")
type(Key.F4, Key.ALT)
run("explorer " + os.path.join(util.desktop, "name with space.htm"))
wait("turbo_webpage.png")
type("q", Key.CTRL + Key.SHIFT)
run('explorer "https://turbo.net/"')
wait("turbo_webpage.png")
wait(5)
click("turbo_webpage.png") # To gain focus.
wait(10)
type("p", Key.CTRL)
wait("print_window.png")
click("print_print.png")
wait("print_location.png")
type(save_location + Key.ENTER)
assert(util.file_exists(save_location, 5))

type(Key.ESC)
type("q", Key.CTRL + Key.SHIFT)
sleep(5)

# Check if the session terminates.
util.check_running()
