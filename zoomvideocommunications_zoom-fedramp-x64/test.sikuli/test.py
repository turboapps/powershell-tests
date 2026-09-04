# The tests for zoomvideocommunications/zoom and zoomvideocommunications/zoom-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("zoom_window.png")
run("turbo stop test")
wait(10)

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Zoom", "Zoom Workplace.lnk"))
wait("zoom_window.png")
if exists("dont-show-vdi.png",10):
    click("dont-show-vdi.png")
click("sign-in.png")
wait("down-arrow.png")
wait(5)
click("down-arrow.png")
wait("zoomgov-com.png")
click("zoomgov-com.png")
type(Key.F4, Key.ALT)
wait(10)
if exists("systray-arrow.png"):
    click("systray-arrow.png")
    wait(5)
    if exists("zoom-systray.png"):
        hover("zoom-systray.png")
        
# URL handler.
run('explorer "https://zoom.us/test"')
wait("join-test-button.png")
click("join-test-button.png")
# The Edge external-protocol dialog ("Open Zoom Workplace?") can take longer
# than the default wait to appear, and the Join click is occasionally swallowed
# while the page is still settling. Give it a longer window, then click again.
if not exists("url-handler-checkbox.png",60):
    click("join-test-button.png")
wait("url-handler-checkbox.png",60)
click("url-handler-checkbox.png")
type(Key.TAB)
wait(2)
type(Key.TAB)
wait(2)
type(Key.ENTER)
wait("join-mtg.png")
click("join-mtg.png")
wait("yes-sound.png")
click("yes-sound.png")
wait("yes-sound.png")
click("yes-sound.png")
wait("end-test.png")
click("end-test.png")
util.close_app("Edge")
if exists("systray-arrow.png"):
    click("systray-arrow.png")
    wait(5)
    rightClick("zoom-systray.png")
    click("exit-zoom.png")
wait(20)

# Check if the session terminates.
util.check_running()
