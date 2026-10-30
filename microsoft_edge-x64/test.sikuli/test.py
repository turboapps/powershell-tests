script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

save_location = os.path.join(util.desktop, "print.pdf")

# google.com serves two homepages at random: the classic one with a "Google
# Search" button (webpage.png) and a newer one with "Create images / Ask about
# files / Brainstorm" chips and no such button. The header strip (Gmail,
# Images, apps, Sign in) is on both. 0.85 because Edge's own new-tab page,
# which has a Sign in button too, scores 0.70 against it.
google_anchors = [Pattern("google_header.png").similar(0.85), Pattern("webpage.png").similar(0.60)]

def wait_google(timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        for anchor in google_anchors:
            match = exists(anchor, 0)
            if match:
                return match
        wait(1)
    return wait(google_anchors[0], 0)  # FindFailed names the header anchor

# Test of `turbo run`.
wait("new-tab.png")
run("turbo stop test")
wait(10)

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Microsoft Edge.lnk"))
wait("new-tab.png")
click("new-tab.png")

# Activate and maximize the app window.
app_window = App().focus("Edge")
if app_window.isValid():
    type(Key.UP, Key.WIN)

# Basic operations.
click(Pattern("address-bar.png").targetOffset(16,1))
if exists("about-blank.png",5):
    click("about-blank.png")
type("https://google.com/" + Key.ENTER)
wait_google()
wait(3)
type("s", Key.CTRL)
wait("save_type.png")
type(os.path.join(util.desktop, "name with space"))
click("save_type.png")
click("save_type_correct.png")
type(Key.ENTER)
wait(20)
type(Key.ESC)
assert(os.path.exists(os.path.join(util.desktop, "name with space.html")),60)
if App("Edge").isRunning(10):
    util.close_app("Edge")

# Set default browser.
#
# The Settings search list fills in while it is typed into: in App Tests run
# 38808753015 the "Default apps" row was found 2nd in a partial list (Display
# settings / Default apps / Duplicate ...), the list was re-sorted before the
# click landed, and the click opened row 2 of the final list, "Choose a default
# app for each type of file". So find the row only once it holds still, prove
# the Default apps page opened (its Web browser tile), and on a wrong page close
# Settings and search again. Win+Up instead of clicking the maximize button: it
# is a no-op on a window that is already maximized, where the button would
# restore it.
def open_default_apps(attempts=3):
    for attempt in range(attempts):
        type("i", Key.WIN)
        wait("windows_setting_window.png")
        type("Default apps")
        click(util.find_settled("windows_setting_default.png"))
        wait(3)
        type(Key.UP, Key.WIN)
        browser_tile = exists("windows_setting_default_browser.png", 15)
        if browser_tile:
            return browser_tile
        Debug.user("open_default_apps: Default apps page did not open on attempt %d of %d"
                   % (attempt + 1, attempts))
        type(Key.F4, Key.ALT)
        wait(3)
    raise FindFailed("open_default_apps: Default apps page never opened in %d attempts" % attempts)

click(open_default_apps())
wait(2)
click(Pattern("windows_setting_default_edge.png").similar(0.95))
type(Key.F4, Key.ALT)
run("explorer " + os.path.join(util.desktop, "name with space.html"))
wait_google()
if App("Edge").isRunning(10):
    util.close_app("Edge")
run('explorer "https://google.com/"')
# To gain focus: blank page below the anchor, never the header links.
click(wait_google().getTarget().offset(0, 200))
wait(5)
type("p", Key.CTRL)
wait("print_window.png")
# Edge 157 is rolling out a redesigned print preview: settings on the right,
# a white Cancel set apart from Print, and Print in the accent colour (blue
# on some VMs, black on others). The same build serves either layout per
# profile, so look for both. print_print_new.png scores 0.88-1.00 on the new
# layout, 0.79 on the old one and 0.65 while Print is still greyed out during
# "Loading preview", so it is never clicked before the preview is ready.
print_buttons = [Pattern("print_print.png").targetOffset(-64,1),
                 Pattern("print_print_new.png").similar(0.80).targetOffset(-35,0)]
def find_print_button(timeout=30):
    end = time.time() + timeout
    while time.time() < end:
        for button in print_buttons:
            match = exists(button, 0)
            if match:
                return match
        wait(1)
    return wait(print_buttons[1], 0)  # FindFailed names the new-layout button
click(find_print_button())
wait("print_location.png")
wait(2)
paste(save_location)
wait(2)
type(Key.ENTER)
assert(util.file_exists(save_location, 5))

click("menu.png")
click(Pattern("menu_content.png").targetOffset(0,-14))
wait("setting_page.png")
wait(10)

# Check "help".
type(Key.F1)
wait("help_url.png")
if App("Edge").isRunning(10):
    util.close_app("Edge")
wait(20)

# Check if the session terminates.
util.check_running()
