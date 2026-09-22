# The tests for irfanview/irfanview, irfanview/irfanview-x64 and irfanview/irfanview-arm64 are the same except for the shortcut.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

save_path = os.path.join(util.desktop, "red fox.bmp")

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("irfanview-menu.png")
wait(3)
run("turbo stop test")

# Launch the app. The desktop shortcut name comes from the image, not the test,
# and it moves: irfanview-arm64 shipped "IrfanView.lnk" when this test was
# written, "IrfanView ARM64.lnk" by 4.75, and "IrfanView.lnk" again in 4.76.
# Resolve before launching - explorer with a missing path does not fail, it
# silently opens a Documents window and the test then dies at an unrelated
# wait() further down, pointing at the wrong thing.
util.launch_shortcut("IrfanView ARM64.lnk", "IrfanView.lnk", base=util.desktop)
wait("irfanview-menu.png")
click("irfanview-menu.png")

# Basic operations.
type("o")
wait("file-open.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("fox-open.png")
type("g", Key.CTRL) # Invert greyscale.
wait("grey-fox.png")
type("s")
wait(3)
type(save_path)
wait(3)
type(Key.ENTER)
util.file_exists(save_path, 5)

# Check "help".
type(Key.F1)
wait("help-open.png")
type(Key.F4, Key.ALT) # Close help.
wait(3)
type(Key.ESC) # Close app.
wait(3)
type(Key.ESC) # Close app.
wait(3)

# Test file association.
run("explorer " + save_path)
click("openwith-irfanview.png")
click("always-use.png")
wait("grey-fox.png")
type(Key.ESC) # Close app.
wait(3)
run("explorer " + save_path)
wait("grey-fox.png")
click("grey-fox.png")
type(Key.ESC) # Close app
wait(20)

# Check if the session terminates.
util.check_running()