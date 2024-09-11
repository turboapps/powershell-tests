script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

dwgfile_path = os.path.join(script_path, os.pardir, "resources", "blocks_and_tables_-_metric.dwg")

setAutoWaitTimeout(60)
util.pre_test()

# Test of `turbo run`.
wait("app-loaded.png")
app_window = App().focus("Autodesk DWG TrueView 2025") # Activate and maximize the app window.
if app_window.isValid():
    type(Key.UP, Key.WIN)
    type(Key.UP, Key.WIN)
wait(3)
type(Key.F4, Key.ALT) # Close app.
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "DWG TrueView"))
wait("app-loaded.png")
app_window = App().focus("Autodesk DWG TrueView 2025") # Activate and maximize the app window.
if app_window.isValid():
    type(Key.UP, Key.WIN)
    type(Key.UP, Key.WIN)
wait(3)
click("app-loaded.png") # To gain focus.
click(Pattern("app-loaded.png").targetOffset(-51,49))
wait("file-open.png")
click("file-open.png")
type(dwgfile_path + Key.ENTER)
wait("dwg-tab.png")
wait(5)
type(Key.F1)
wait("help.png",120)
wait(5)
type(Key.F4, Key.ALT) # Close help.
wait(5)
type(Key.F4, Key.ALT) # Close app.
wait(5)
os.system('cmd /c taskkill /f /im "AcHelp2.exe" /t')
os.system('cmd /c taskkill /f /im "ADPClientService.exe" /t')

# Test file association.
run("explorer " + dwgfile_path)
wait("dwg-tab.png")
type(Key.F4, Key.ALT) # Close app.
wait(10)
os.system('cmd /c taskkill /f /im "ADPClientService.exe" /t')
wait(20)

# Check if the session terminates.
util.check_running()