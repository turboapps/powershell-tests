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
if exists("upgrade-ok.png",60):
    click("upgrade-ok.png")
wait("zoom_window.png")
run("turbo stop test")
wait(10)

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Zoom", "Zoom Workplace.lnk"))
if exists("upgrade-ok.png",60):
    click("upgrade-ok.png")
wait("zoom_window.png")
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
wait("URL_handler_1.png")
click(Pattern("URL_handler_2.png").targetOffset(-40,0))
wait("join-mtg.png")
click("join-mtg.png")
wait("yes-sound.png")
click("yes-sound.png")
wait("yes-sound.png")
click("yes-sound.png")
wait("end-test.png")
click("end-test.png")
closeApp("Edge")
if exists("systray-arrow.png"):
    click("systray-arrow.png")
    wait(5)
    rightClick("zoom-systray.png")
    click("exit-zoom.png")
wait(20)

# Check if the session terminates.
util.check_running()
