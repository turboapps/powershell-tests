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
util.close_firewall_alert_continue()
wait("new_tab.png")
run("turbo stop test")
wait(10)

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Microsoft Edge.lnk"))
util.close_firewall_alert_continue()
wait("new_tab.png")

# Activate and maximize the app window.
app_window = App().focus("Edge")
if app_window.isValid():
    type(Key.UP, Key.WIN)

# Basic operations.
click(Pattern("address-bar.png").targetOffset(28,-1))
type("https://turbo.net/" + Key.ENTER)
wait("turbo_webpage.png")
wait(3)
type("s", Key.CTRL)
wait("save.png")
type(os.path.join(util.desktop, "name with space"))
click("save_type.png")
click("save_type_correct.png")
type(Key.ENTER)
wait("download_complete.png")
wait(20)
type(Key.ESC)
assert(os.path.exists(os.path.join(util.desktop, "name with space.html")))
type(Key.F4, Key.ALT)

# Set default browser.
type("i", Key.WIN)
wait("windows_setting_window.png")
type("Default apps")
click("windows_setting_default.png")
click(Pattern("maximize_default_window.png").targetOffset(-2,-4))
wait(5)
click("windows_setting_default_browser.png")
wait(2)
click(Pattern("windows_setting_default_edge.png").similar(0.95))
type(Key.F4, Key.ALT)
run("explorer " + os.path.join(util.desktop, "name with space.html"))
wait("turbo_webpage.png")
type(Key.F4, Key.ALT)
run('explorer "https://turbo.net/"')
wait("turbo_webpage.png")
click("turbo_webpage.png") # To gain focus.
wait(5)
type("p", Key.CTRL)
wait("print_window.png")
click(Pattern("print_print.png").targetOffset(-64,1))
wait("print_location.png")
type(save_location + Key.ENTER)
assert(util.file_exists(save_location, 5))

click(Pattern("menu.png").targetOffset(90,0))
click(Pattern("menu_content.png").targetOffset(0,-14))
wait("setting_page.png")

# Check "help".
type(Key.F1)
wait("help_url.png")
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()
