script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

save_path = os.path.join(util.desktop, "red fox.jpg")

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait(Pattern("gimp-menus.png").similar(0.90), 90)
app_window = App().focus("GNU Image Manipulation Program") # Activate and maximize the app window.
if app_window.isValid():
    type(Key.UP, Key.WIN)
wait(3)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "GIMP"))
wait(Pattern("gimp-menus.png").similar(0.90), 90)
app_window = App().focus("GNU Image Manipulation Program") # Activate and maximize the app window.
if app_window.isValid():
    type(Key.UP, Key.WIN)
wait(3)

# Basic operations.
type("o", Key.CTRL)
wait("desktop-folder.png")
click("desktop-folder.png")
click("type-path-button.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("red-fox.png")
click("colors-menu.png")
wait("invert-tool.png")
click("invert-tool.png")
wait("fox-inverted.png")
wait(5)
type("e", Key.CTRL + Key.SHIFT)
wait("export-button.png")
type("a", Key.CTRL)
type(save_path + Key.ENTER)
wait(5)
wait("export-image.png")
click("export-image.png")

# Check "help".
type(Key.F1)
wait("read-online-button.png")
click("read-online-button.png")
wait("gimp-help.png")
wait(3)
type(Key.F4, Key.ALT) # Close help.
wait(3)
util.file_exists(save_path, 5) # Export might be slow.
type(Key.F4, Key.ALT) # Close GIMP.
wait("discard-changes.png")
click("discard-changes.png")
wait(3)

# Test file association.
run("explorer " + save_path)
wait("select-gimp-app.png")
click("select-gimp-app.png")
click(Pattern("always-open-chkbox.png").targetOffset(-126,1))
click("ok-button.png")
wait("fox-inverted.png", 90)
type(Key.F4, Key.ALT)
wait(3)
run("explorer " + save_path)
wait(Pattern("inverted-fox-open.png").similar(0.90), 90)
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()