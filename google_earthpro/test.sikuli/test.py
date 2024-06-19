script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# Test of `turbo run`.
click(Pattern("DX_mode.png").targetOffset(33,21))
wait("compass.png")
wait(3)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.desktop, "Google Earth Pro"))

# Basic operations.
click(Pattern("DX_mode.png").targetOffset(33,21))
wait("compass.png")
wait(3)
type("s", Key.CTRL + Key.ALT)
wait("save-image-button.png")
click("save-image-button.png")
wait(5)
type(os.path.join(util.desktop, "The world") + Key.ENTER)
if not exists("expand-places.png"):
    click("places.png")
click(Pattern("expand-places.png").targetOffset(-22,-2))
doubleClick("eiffel-tower.png")
rightClick("eiffel-tower-highlighted.png")
click("save-place-as.png")
wait(5)
type(os.path.join(util.desktop, "eiffel tower") + Key.ENTER)
type(Key.F4, Key.ALT)
wait(5)
run("explorer " + os.path.join(util.desktop, "eiffel tower.kmz"))
click(Pattern("DX_mode.png").targetOffset(33,21))
wait("compass.png")
type(Key.F4, Key.ALT)
wait("discard.png")
click("discard.png")
wait(10)

# Check if the session terminates.
util.check_running()