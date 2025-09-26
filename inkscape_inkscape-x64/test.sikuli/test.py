# The tests for inkscape/inkscape and inkscape/inkscape-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

save_path = os.path.join(util.desktop, "test.svg")

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("setup.png", 60)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Inkscape", "Inkscape.lnk"))
wait("setup.png", 60)
click("setup_save.png")
if exists("support_thanks.png"):
    click("support_thanks.png")

# Basic operations.
click("new.png")
wait("tools.png")
wait(2)
click(Pattern("tools.png").targetOffset(-87,-21))
dragDrop(Pattern("empty_canvas.png").targetOffset(-90,-66), Pattern("empty_canvas.png").targetOffset(61,56))
wait("results_1.png")
type("s", Key.CTRL)
wait("save_location.png")
paste(util.desktop)
type(Key.ENTER)
wait(3)
paste("test")
type(Key.ENTER)
assert(util.file_exists(save_path, 5))
type("w", Key.CTRL)
wait("empty_canvas.png")
type("o", Key.CTRL)
click(Pattern("open_location.png").targetOffset(35,-13))
paste(save_path)
type(Key.ENTER)
wait("results_2.png")

# Check "help".
click(Pattern("menu.png").targetOffset(77,0))
click(Pattern("menu_help.png").targetOffset(-6,-24))
wait("help_url.png")
closeApp("Edge")
wait(10)
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()