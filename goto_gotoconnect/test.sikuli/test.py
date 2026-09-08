script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("goto_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "GoTo.lnk"))
wait("goto_window.png")
wait(5)

# There is an issue that when the app is not fully closed (taskbar tray is on),
# URL handler will not work. It is a native behavior.
#
# The single click on File is lost when the pool VM is contended: the menu bar
# takes it as a window-activation click and latches File without ever opening
# the dropdown, so the Quit item below is searched for the full 30 s and never
# appears. That is the whole of this test's CI failure - 5 of 8 full-suite runs
# across five different pool VMs, while 4 of 4 isolated dispatches passed.
# Activate the window first, and re-open the menu until the dropdown is really
# there. A run that exhausts the attempts still fails on the Quit item below,
# with the same diagnosis it has today.
util.activate_app_window("GoTo", 10)
wait(1)
for attempt in range(5):
    click(Pattern("menu.png").targetOffset(-96,1))
    if exists("menu_file.png", 5):
        break
    type(Key.ESC)
    wait(1)
    util.activate_app_window("GoTo", 10)
    wait(1)
click("menu_file.png")
wait(10)

# URL handler.
run('explorer "https://google.com"')
wait(10)
util.close_app("Edge")
run('explorer "https://global.gotomeeting.com/join/750803053"')
if exists("join-from-desktop.png",10):
    click("join-from-desktop.png")
wait("url-prompt.png")
click("url-prompt.png")
wait(5)
util.close_app("Edge")
wait("join_meeting.png")
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()