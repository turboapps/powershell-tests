script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Test of `turbo run`.
wait("r_window.png",60)
run("turbo stop test")
if exists("save_ws.png"):
    click(Pattern("save_ws.png").targetOffset(6,54))

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(os.path.join(util.start_menu, "R"), "R"))

# Basic operations.
wait("r_window.png",60)
click("r_window.png")
type('install.packages("tidyverse")' + Key.ENTER)
wait("cran_source.png")
click(Pattern("cran_source_ok.png").targetOffset(-36,4))
wait("r_console_pac_installed.png", 120)
type("library(tidyverse)" + Key.ENTER)
wait("r_console_lib_imported.png", 150)
type("1 + 2" + Key.ENTER)
wait("math.png")

# Check "help".
click(Pattern("menu.png").targetOffset(30,-2))
click("menu_help.png")
wait("help_window.png")
click("help_window.png")
wait(3)
type(Key.ENTER)
wait(3)
type(Key.F4, Key.ALT)
wait("save_ws.png")
click("save_ws.png")
wait(10)

# Check if the session terminates.
util.check_running()