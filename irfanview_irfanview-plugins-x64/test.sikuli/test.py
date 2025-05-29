# The tests for irfanview/irfanview-plugins and irfanview/irfanview-plugins-x64 are the same except for the shortcut.

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

# Launch the app.
run("explorer " + os.path.join(util.desktop, "IrfanView 64.lnk"))
wait("irfanview-menu.png")
app_window = App().focus("IrfanView") # Activate and maximize the app window.
if app_window.isValid():
    type(Key.UP, Key.WIN)
wait(3)
type("o")
wait("file-open.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("fox-open.png")

# Test JXL plugin
type("o")
wait("file-open.png")
type(os.path.join(script_path, os.pardir, "resources", "splines.jxl") + Key.ENTER)
wait("splines.png")
wait(5)
type(Key.F4, Key.ALT) # Close app.
wait(10)

# Check if the session terminates.
util.check_running()