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
wait(5)

# Activate and maximize the app window.
app_window = App().focus("Chromium")
if app_window.isValid():
    type(Key.UP, Key.WIN)

# Basic operations.
type("l", Key.CTRL)
paste("https://google.com/")
type(Key.ENTER)
wait("google-signin.png")
wait(3)
type("s", Key.CTRL)
wait("save_type.png")
paste(os.path.join(util.desktop, "name with space"))
click("save_type.png")
click("save_type_correct.png")
type(Key.ENTER)
assert(util.file_exists(os.path.join(util.desktop, "name with space.html"), 10))
type(Key.ESC)
type("l", Key.CTRL)
wait(3)
paste("chrome://settings/")
type(Key.ENTER)
wait("settings_page.png")

# Check "help".
type(Key.F1)
wait("help_page.png")

# Check "print"
type("p", Key.CTRL)
# print_window.png is the Destination row on its own, not the whole settings
# column, because the rest of that column is not invariant.
#
# Chrome adds a "See more" destination link under the Destination row once
# printer enumeration finishes, which pushes Pages / Layout / Color / More
# settings down ~50 px, and the heading counts the sheets the page being printed
# needs - "1 sheet of paper" for google.com against the "11 sheets" of the
# capture the old reference came from. A reference spanning all of that scored
# only 0.78 against a settled dialog whose enumeration had not finished yet and
# 0.45 against one where it had, so whether this wait won that race decided the
# run.
#
# It lost in App Tests runs 35678863980 and 35685507781 (canary): both failure
# screenshots show the print dialog fully open with the See more link, both
# score the old reference at 0.45 and the new one at 0.94, and both spent the
# whole 60 s budget on an image that layout can no longer match. Run 35168175666
# (chrome) died at this same line on this same image; its artifact has expired,
# so only the two canary runs are confirmed by picture.
#
# The Destination row sits above the insertion point and carries no counted
# text, so it scores 0.94 against both layouts and 0.45-0.55 while the dialog is
# still painting its spinner - which is the "the dialog is up and ready" signal
# this wait wanted, and the old reference only ever gave by accident.
wait("print_window.png")
click(Pattern("print_print.png").targetOffset(-28,8))
wait("print_location.png")
paste(save_location)
type(Key.ENTER)
assert(util.file_exists(save_location, 5))
wait(5)
type(Key.ESC)
type(Key.F4, Key.ALT)

# Set default browser.
type("i", Key.WIN)
wait("windows_setting_window.png")
type("Default apps")
wait(3)
type(Key.ENTER)
click("default-search-apps.png")
paste("chromium")
type(Key.ENTER)
click("windows_setting_default_browser_chrome.png")
click("set-default.png")
wait(5)
type(Key.F4, Key.ALT)
# Test FTA launch
run("explorer " + os.path.join(util.desktop, "name with space.html"))
wait("google-signin.png")
wait(5)
app_window = App().focus("Chromium")
type(Key.F4, Key.ALT)
# Test protocol handler launch
run('explorer "https://google.com/"')
wait("google-signin.png")
wait(5)
app_window = App().focus("Chromium")
type(Key.F4, Key.ALT)
wait(15)

# Check if the session terminates.
util.check_running()