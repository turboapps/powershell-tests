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
html_location = os.path.join(util.desktop, "name with space.html")

# Remove leftover output files from a previous run. The save-as and the print step
# are each verified with util.file_exists against a fixed path, so a stale file
# satisfies the assert even when the current save failed: the test then limps past
# the real failure and dies later at an unrelated step (the saved page reopening
# blank). A leftover .html also stops the Save As dialog on an overwrite prompt.
for leftover in [save_location, html_location]:
    if os.path.exists(leftover):
        os.remove(leftover)

# Test of `turbo run`.
wait("chrome_window.png")
wait(5)
util.close_app("Chrome")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Google Chrome.lnk"))
wait("chrome_window.png")

# Activate and maximize the app window.
app_window = App().focus("Chrome")
if app_window.isValid():
    type(Key.UP, Key.WIN)

# Basic operations.
type("l", Key.CTRL)
paste("https://google.com/")
type(Key.ENTER)
wait("webpage.png")
wait(3)
type("s", Key.CTRL)
wait("save_type.png")
wait(3)
paste(os.path.join(util.desktop, "name with space"))
click("save_type.png")
click("save_type_correct.png")
type(Key.ENTER)
assert(util.file_exists(html_location, 10))
type(Key.ESC)
type("l", Key.CTRL)
paste("chrome://settings/")
type(Key.ENTER)
wait("settings_page.png")

# Check "help".
type(Key.F1)
wait("help_page.png")
util.close_app("Chrome")

# Set default browser.
type("i", Key.WIN)
wait("windows_setting_window.png")
paste("Default apps")
wait(3)
type(Key.ENTER)
click(Pattern("search-apps.png").targetOffset(-91,30))
paste("google")
wait(5)
click("windows_setting_default_browser_chrome.png")
wait("set-default.png")
click("set-default.png")
wait(5)
type(Key.F4, Key.ALT)
run("explorer " + html_location)
wait("webpage.png")
util.close_app("Chrome")
run('explorer "https://google.com/"')
wait("webpage.png") # To gain focus.
wait(2)
App().focus("Google Chrome")
wait(5)
type("n", Key.CTRL)
wait(5)
paste("https://google.com")
type(Key.ENTER)
wait(5)
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
wait("print_window.png",60)
click(Pattern("print_print.png").targetOffset(-28,8))
wait("print_location.png")
paste(save_location)
type(Key.ENTER)
assert(util.file_exists(save_location, 5))

type(Key.ESC)
util.close_app("Chrome")
util.close_app("Chrome")
wait(5)

# Check if the session terminates.
util.check_running()