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
if exists("agreement.png"):
    click(Pattern("agreement.png").targetOffset(-52,212))
if exists("tips.png"):
    click(Pattern("tips.png").targetOffset(-122,-19))
    click(Pattern("tips.png").targetOffset(92,23))
wait("ghidra_window.png")
wait("help.png")
wait(5)
click(Pattern("help.png").targetOffset(130,-24))
type(Key.F4, Key.ALT)
run("turbo stop test")
wait(10)

# Launch the app by Start menu shortcut.
run("explorer " + os.path.join(util.start_menu, "Ghidra.lnk"))
if exists("agreement.png"):
    click(Pattern("agreement.png").targetOffset(-52,212))
if exists("tips.png"):
    click(Pattern("tips.png").targetOffset(-122,-19))
    click(Pattern("tips.png").targetOffset(92,23))
wait("ghidra_window.png")

# Check the "help" of the app. In the new version, the first launch opens the help automatically.
wait("help.png")
wait(5)
click(Pattern("help.png").targetOffset(130,-24))
type(Key.F4, Key.ALT)

# Basic operations.
click("ghidra_window.png") # To gain focus.
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
wait("import_summary.png",120)
type(Key.ENTER)
wait("import_imported.png")
type(Key.F4, Key.ALT)

# Test of headless mode.
run('turbo run nsa/ghidra --using eclipse/temurin --isolate=merge-user --trigger headless -- ' + project_path_headless + ' ghidra-project-headless -import ' + import_path + ' -processor x86:LE:64:default -overwrite')
assert(util.file_exists(os.path.join(project_path_headless, "ghidra-project-headless.gpr"), 5))

# Check if the session terminates after closing the app.
util.check_running()