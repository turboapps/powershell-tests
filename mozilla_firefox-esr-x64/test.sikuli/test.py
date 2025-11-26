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
wait("firefox_window.png",60)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Firefox.lnk"))
wait("firefox_window.png")

# Basic operations.
paste("https://google.com/",60)
type(Key.ENTER)
wait(Pattern("webpage.png").similar(0.60))
wait(3)
type("s", Key.CTRL)
wait("save.png")
paste(os.path.join(util.desktop, "name with space"))
click(Pattern("save_type.png").targetOffset(33,-1))
click("save_type_correct.png")
type(Key.ENTER)
assert(util.file_exists(os.path.join(util.desktop, "name with space.htm"), 20))
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
click("windows_setting_default.png") # To gain focus.
click("windows_setting_default.png")
paste("Default apps")
type(Key.ENTER)
wait(3)
click("set-default-app.png")
wait(3)
click("search-apps.png")
paste("firefox")
click("windows_setting_default_firefox.png")
wait(3)
click("set-default.png")
wait(3)
type(Key.F4, Key.ALT)
run("explorer " + os.path.join(util.desktop, "name with space.htm"))
wait(Pattern("webpage.png").similar(0.60))
type("q", Key.CTRL + Key.SHIFT)
run('explorer "https://google.com/"')
wait(Pattern("webpage.png").similar(0.60))
wait(5)
click(Pattern("webpage.png").similar(0.60)) # To gain focus.
wait(10)
app_window = App().focus("Firefox")
if app_window.isValid():
    type("p", Key.CTRL)
wait(Pattern("print_window.png").similar(0.60))
click("print_print.png")
wait("print_location.png")
paste(save_location)
click(Pattern("print_save.png").targetOffset(-49,-1))
assert(util.file_exists(save_location, 5))

type(Key.ESC)
type("q", Key.CTRL + Key.SHIFT)
sleep(5)

# Check if the session terminates.
util.check_running()