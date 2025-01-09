# The tests for google/chrome and google/chrome-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

docs = os.path.join((os.environ["USERPROFILE"]), "Documents")

# Test of `turbo run`.
wait("hec-ras-agree.png")
type(Key.F4, Key.ALT)
wait(5)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(os.path.join(util.start_menu, "HEC", "HEC-RAS"), "HEC-RAS"))
wait("hec-ras-agree.png")
click("hec-ras-agree.png")
click("eula-next.png")
wait(10)

# Basic operations.
type("f", Key.ALT)
click("open-project.png")
click("def-project-folder.png")
doubleClick("siam-example.png")
doubleClick("select-project.png")
wait(5)
click("view-data.png")
wait("data-set.png")
type(Key.F4, Key.ALT)
wait(3)
type(Key.F4, Key.ALT)
wait(5)

# Check if the session terminates.
util.check_running()