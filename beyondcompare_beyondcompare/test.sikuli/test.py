script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

resources_path = os.path.join(script_path, os.pardir, "resources")

setAutoWaitTimeout(20)
util.pre_test()

# Test of `turbo run`.
wait("bc_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Beyond Compare 4", "Beyond Compare 4.lnk"))

# Basic operations.
click(Pattern("bc_window.png").targetOffset(139,29))
click(Pattern("source1.png").targetOffset(23,17))
type(os.path.join(resources_path, "file1.txt") + Key.ENTER)
click(Pattern("source2.png").targetOffset(82,-3))
type(os.path.join(resources_path, "file2.txt") + Key.ENTER)
wait("diff.png")

# Check "help".
type(Key.F1)
wait("help_window.png")
type(Key.F4, Key.ALT) # Close the help window.
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
wait(10)
util.check_running()