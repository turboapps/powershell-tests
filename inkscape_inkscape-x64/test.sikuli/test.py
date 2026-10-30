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
# The new-document window paints its toolbox first and docks the default
# "Fill and Stroke" panel afterwards. When the panel arrives the canvas narrows
# and the page re-centres about 190 px to the left. The old fixed wait(2) was
# usually enough, but in App Tests run 40980991791 the panel was still missing
# 5 s after the toolbox appeared: the rectangle drag was aimed at the pre-dock
# page, the relayout landed mid-drag, and Inkscape drew a 13.6 mm wide sliver
# instead of the 55.6 mm rectangle, so results_1.png never matched. Wait for
# the dock, then for the rectangle toolbar (Rx/Ry) to prove the tool switch was
# processed, and aim the drag at a canvas match that has stopped moving.
# PROBE (do not merge): close the dock so the fixed test must fail at the dock wait.
click(Pattern("dock_fill_stroke.png").targetOffset(49,0))
wait(3)
wait("dock_fill_stroke.png", 60)
click(Pattern("tools.png").targetOffset(-87,-21))
wait(Pattern("rect_toolbar.png").similar(0.85))
canvas = util.find_settled("empty_canvas.png").getTarget()
dragDrop(canvas.offset(-90,-66), canvas.offset(61,56))
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
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()