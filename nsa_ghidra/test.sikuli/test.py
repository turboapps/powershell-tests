script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(60)
project_path = os.path.join(util.desktop, "ghidra-test")
project_path_headless = os.path.join(util.desktop, "ghidra-test-headless")
import_path = os.path.join(script_path, os.pardir, "resources", "HelloWorld.exe")

util.pre_test()

# `turbo run` should launch the app.
wait("ghidra_window.png")
run("turbo stop test")

# Launch the app by Start menu shortcut.
run("explorer " + os.path.join(util.start_menu, "Ghidra.lnk"))
wait("ghidra_window.png")

# Check the "help" of the app.
type(Key.F1)
wait("help.png")
wait(5)
click(Pattern("help.png").targetOffset(125,-47))
type(Key.F4, Key.ALT)

# Basic operations.
type("n", Key.CTRL)
wait("new_project_1.png")
click("new_project_next.png")
click("new_project_2.png")
type("a", Key.CTRL)
type(project_path)
type(Key.TAB + Key.TAB)
type("ghidra-test")
click("new_project_finish.png")

wait("new_project_created.png")
type("i")
wait("import_location.png")
type(import_path + Key.ENTER)
click(Pattern("import_details.png").targetOffset(-37,94))
util.close_firewall_alert()
wait("import_summary.png")
type(Key.ENTER)
wait("import_imported.png")
type(Key.F4, Key.ALT)

# Test of headless mode.
run('turbo run nsa/ghidra --using eclipse/temurin --isolate=merge-user --trigger headless -- ' + project_path_headless + ' ghidra-project-headless -import ' + import_path + ' -processor x86:LE:64:default -overwrite')
util.close_firewall_alert()
assert(util.file_exists(os.path.join(project_path_headless, "ghidra-project-headless.gpr"), 5))

# Check if the session terminates after closing the app.
util.check_running()