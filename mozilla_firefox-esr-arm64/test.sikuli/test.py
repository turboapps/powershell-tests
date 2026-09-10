# The tests for mozilla/firefox-esr, mozilla/firefox-esr-x64 and mozilla/firefox-esr-arm64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

save_location = os.path.join(util.desktop, "print.pdf")
htm_location = os.path.join(util.desktop, "name with space.htm")

# Remove artifacts a previous run may have left on the desktop. Both saves below
# are judged by whether the file appeared; a stale name with space.htm or
# print.pdf would pass that check even when the current save/print failed,
# letting the test limp past a broken interaction and only FindFail later. It
# would also rob save_page_as_html of the signal it retries on.
for stale in (htm_location, save_location):
    if os.path.exists(stale):
        os.remove(stale)

# Test of `turbo run`.
wait("firefox_window.png",60)
run("turbo stop test")

# Launch the app.
util.launch_shortcut("Firefox.lnk", "Firefox ESR ARM64.lnk")
wait("firefox_window.png",60)

# Basic operations.
type("l", Key.CTRL)
wait(2)
paste("https://google.com/")
type(Key.ENTER)
wait(Pattern("webpage.png").similar(0.60))
wait(3)
util.save_page_as_html("save.png", "save_type.png", os.path.join(util.desktop, "name with space"), htm_location)
type("l", Key.CTRL)
wait(2)
paste("about:preferences")
type(Key.ENTER)
wait("settings_page.png")

# Check "help".
click("help-link.png")
wait("help_page.png")
type("q", Key.CTRL + Key.SHIFT)
util.wait_app_quiet("firefox.exe")

# Set default browser.
#
# search-apps.png is the "Search apps" placeholder on the Default apps page, and
# at SikuliX's default 0.7 it also matches the Windows 11 taskbar Search pill --
# the same grey placeholder text on the same light rounded field. In App Tests run
# 34423171312 that is what happened once Settings failed to leave its Home page:
# the pill matched at 0.714, the click opened Windows Search, every click after it
# landed in that flyout, and the run died at set-default.png four lines later. The
# real field matches at 0.988 in every run measured, so 0.90 separates the two
# with room on either side -- and it is what makes the page check inside
# open_settings_page mean anything, because the pill is on screen whether or not
# the page opened.
search_apps = util.open_settings_page("windows_setting_default.png", "Default apps",
                                      Pattern("search-apps.png").similar(0.90))
click(search_apps)
util.paste_text("firefox")
click("windows_setting_default_firefox.png")
wait(3)
click("set-default.png")
wait(3)
type(Key.F4, Key.ALT)
run("explorer " + htm_location)
if exists("choose-app-firefox.png",10):
    click("choose-app-firefox.png")
    click("always.png")
wait(Pattern("webpage.png").similar(0.60))
type("q", Key.CTRL + Key.SHIFT)
util.wait_app_quiet("firefox.exe")
run('explorer "https://google.com/"')
if exists("open-with-firefox.png",10):
    click("open-with-firefox.png")
    click("always.png")
wait(Pattern("webpage.png").similar(0.60))
wait(5)
click(Pattern("webpage.png").similar(0.60)) # To gain focus.
wait(10)
app_window = App().focus("Firefox")
if app_window.isValid():
    type("p", Key.CTRL)
wait(Pattern("print_window.png").similar(0.60))
click(Pattern("print_print.png").targetOffset(-9,1))
wait("print_location.png")
paste(save_location)
click(Pattern("print_save.png").targetOffset(-49,-1))
assert(util.file_exists(save_location, 5))

type(Key.ESC)
type("q", Key.CTRL + Key.SHIFT)
sleep(5)

# Check if the session terminates.
util.check_running()