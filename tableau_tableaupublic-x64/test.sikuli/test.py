script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("tableau-open.png",120)
click("tableau-open.png")
type(Key.F4, Key.ALT)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Tableau Public"))

# Basic operations.
wait("tableau-open.png",120)
click("tableau-open.png")
type("o", Key.CTRL)
wait("file_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "US_Superstore_10.0.twbx"))
type(Key.ENTER)
wait("workbook-open.png")
click("product-tab.png")
click("furniture.png")
rightClick("furniture-selected.png")
click("keep-only.png")
wait("keep-only-result.png")

# Check "help".
type(Key.F1)
wait("help_url.png")
closeApp("Edge")
wait(10) # Wait for the complete close of the firewall alert.
type(Key.F4, Key.ALT)
if exists("save-changes-prompt.png"):
    click(Pattern("save-changes-prompt.png").targetOffset(14,27))
wait(20)

# Check if the session terminates.
util.check_running()