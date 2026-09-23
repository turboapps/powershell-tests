script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()


def dismiss_announcement():
    """Close the announcement balloon Earth opens over the 3D view, if it is up.

    The balloon is server-pushed content that Earth fetches a few seconds into a
    launch and drops on top of the compass, so whichever of the two renders first
    decides whether the compass can ever be matched.  It never closes by itself.
    """
    balloon = exists(Pattern("announcement-close.png").similar(0.8), 0)
    if balloon is None:
        return False
    # The reference covers the balloon's top-right corner (close button over the
    # scrollbar head); the close button itself sits at (12, 10) inside it.
    click(Location(balloon.x + 12, balloon.y + 10))
    wait(2)
    return True


def wait_compass(attempts=4, budget=15):
    """Wait for the compass, closing the announcement balloon when it covers it."""
    for attempt in range(attempts):
        if exists("compass.png", budget):
            return
        if not dismiss_announcement():
            wait(2)
    # Nothing left to clear - let SikuliX report the usual FindFailed.
    wait("compass.png")


# Test of `turbo run`.
click(Pattern("DX_mode.png").targetOffset(33,21))
wait_compass()
wait(3)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.desktop, "Google Earth Pro"))

# Basic operations.
click(Pattern("DX_mode.png").targetOffset(33,21))
wait_compass()
wait(3)
if exists("dont-show.png",10):
    click("dont-show.png")
    wait(3)
type("s", Key.CTRL + Key.ALT)
wait("save-image-button.png")
click("save-image-button.png")
wait(5)
paste(os.path.join(util.desktop, "The world"))
type(Key.ENTER)
if not exists("expand-places.png"):
    click("places.png")
click(Pattern("expand-places.png").targetOffset(-22,-2))
doubleClick("eiffel-tower.png")
rightClick("eiffel-tower-highlighted.png")
click("save-place-as.png")
wait(5)
paste(os.path.join(util.desktop, "eiffel tower"))
type(Key.ENTER)
type(Key.F4, Key.ALT)
wait(5)
run("explorer " + os.path.join(util.desktop, "eiffel tower.kmz"))
click(Pattern("DX_mode.png").targetOffset(33,21))
wait_compass()
if exists("trusted-file-warning.png",10):
    click("trusted-file-warning.png")
    wait(5)
type(Key.F4, Key.ALT)
wait("discard.png")
click("discard.png")
wait(10)

# Check if the session terminates.
util.check_running()