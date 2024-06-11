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

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Zoom", "Zoom Workplace.lnk"))
wait("zoom_window.png")
type(Key.F4, Key.ALT)

# URL handler.
run('explorer "https://turbo-net.zoom.us/j/81128361870"')
click(Pattern("url_handler.png").targetOffset(132,50))
closeApp("Edge")
click(Pattern("invalid_meeting.png").targetOffset(130,137))
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()