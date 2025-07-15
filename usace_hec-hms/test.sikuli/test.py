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
wait("hec-eula.png")
type(Key.F4, Key.ALT)
wait(5)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(os.path.join(util.start_menu, "HEC", "HEC-HMS"), "HEC-HMS"))
wait("hec-eula.png")
dragDrop(Pattern("hec-eula.png").targetOffset(206,-90), Pattern("hec-eula.png").targetOffset(207,90))
click("eula-agree.png")
click("eula-ok.png")
wait(10)

# Basic operations.
type("h", Key.ALT)
click("install-sample-projects.png")
wait(3)
type(Key.ENTER)
wait(10)
type("o", Key.CTRL)
click("browse.png")
type(docs  + "\\samples\\samples\\river_bend\\river_bend.hms" + Key.ENTER)
wait("basin-models.png")
doubleClick("basin-models.png")
click("min-facitlity.png")
wait("basin-model.png")
wait(5)
type(Key.F4, Key.ALT)
wait(5)

# Check if the session terminates.
util.check_running()