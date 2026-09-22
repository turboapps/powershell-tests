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
# This only says the binary downloads have landed, not that the install is
# over: install.packages("tidyverse") prints "The downloaded binary packages
# are in" and then goes on to build the packages CRAN ships as sources only
# (tinytex, selectr), which keeps the console busy with no prompt for minutes.
# r_console_pac_installed.png reads "The downloaded source packages are in" and
# matches that binary line at 0.87 - the two are one word apart - so this wait
# has always been returning on the binary line. Kept as an early signal that the
# install got going at all; the prompt below is what says it finished.
wait("r_console_pac_installed.png", 120)

# Wait for the prompt to come back. The prompt is the only thing on screen that
# says R is idle again, and the source builds above put minutes between it and
# the line waited for above. This used to be click("console.png",90): click()'s
# second argument is a modifier mask, not a timeout, so the prompt got only the
# 20 s setAutoWaitTimeout (and the click was issued with stray modifiers held),
# and runs 35654098667 and 35678863980 both died here with the console still
# showing "installing the source packages 'tinytex', 'selectr'".
click(wait("console.png", 600))
type("library(tidyverse)")
wait(2)
type(Key.ENTER)
wait("r_console_lib_imported.png", 150)
wait(3)
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