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
wait("welcome-close.png",300)
click("welcome-close.png")
click("gimp-menus.png")
type("q", Key.CTRL)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "GIMP"))
wait("welcome-close.png",90)
click("welcome-close.png")
click("gimp-menus.png")
app_window = App().focus("GNU Image Manipulation Program") # Activate and maximize the app window.
if app_window.isValid():
    type(Key.UP, Key.WIN)
wait(3)

# Basic operations.
type("o", Key.CTRL)
wait("desktop-folder.png")
click("desktop-folder.png")
doubleClick("gimp-folder.png")
wait(5)
doubleClick("resources-folder.png")
click("open-file.png")
wait("red-fox.png")
click("colors-menu.png")
wait("invert-tool.png")
click("invert-tool.png")
wait("fox-inverted.png")
wait(5)
type("e", Key.CTRL + Key.SHIFT)
wait("desktop-folder.png")
click("desktop-folder.png")
click("export-button.png")
wait(10)
click("export-button.png")

wait(5)

# Check "help".
type(Key.F1)
wait("read-online-button.png")
click("read-online-button.png")
wait("gimp-help.png")
wait(3)
type(Key.F4, Key.ALT) # Close help.
wait(3)
util.file_exists(save_path, 5) # Export might be slow.
click("gimp-menus.png")
type("q", Key.CTRL) # Close GIMP.
wait("discard-changes.png")
click("discard-changes.png")
wait(3)

# Set default app.
type("i", Key.WIN)
wait("windows_setting_window.png")
paste("Default apps")
wait(3)
type(Key.ENTER)
click("search-file-type.png")
paste(".jpg")
wait(2)
type(Key.ENTER)
click("jpg-type.png")
click("select-gimp-app.png")
click("set-default.png")
wait(2)
type(Key.F4, Key.ALT)

# Test file association.
run("explorer " + save_path)
wait("fox-inverted.png",90)
type("q", Key.CTRL) # Close GIMP.
wait(3)
run("explorer " + save_path)
wait("inverted-fox-open.png",90)
type("q", Key.CTRL) # Close GIMP.
wait(20)

# Check if the session terminates.
util.check_running()