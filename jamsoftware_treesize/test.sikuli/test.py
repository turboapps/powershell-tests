# The tests for google/chrome and google/chrome-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("license-prompt.png")
type(Key.F4, Key.ALT)
wait(5)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(os.path.join(util.start_menu, "TreeSize"), "TreeSize"))
wait("license-prompt.png")
click("license-ok.png")
wait("select-scan-target.png")
type("f", Key.ALT)
type("t")
click("directory.png")
click("desktop.png")
click("confirm-selection.png")
wait("include-folder.png")
wait(5)
# Close app
type(Key.F4, Key.ALT)

# Test shell context menu
run("explorer c:\\")
rightClick("sikuli-folder.png")
click("treesize-context-menu.png")
if exists("continue-with-trial.png"):
    click("continue-with-trial.png")
wait("program-files.png")
wait(3)
type(Key.F4, Key.ALT)
wait(3)
rightClick("sikuli-folder.png")
click("adv-file-search.png")
wait("search-configuration.png")
wait(10)
type(Key.F4, Key.ALT)
wait(3)
rightClick("sikuli-folder.png")
click("find-dup-files.png")
wait("duplicate-file-search.png")
wait(10)
type(Key.F4, Key.ALT)
wait(3)
rightClick("sikuli-folder.png")
click("find-files-context.png")
wait("basic-search.png")
wait(10)
type(Key.F4, Key.ALT)
wait(5)
# Check if the session terminates.
util.check_running()