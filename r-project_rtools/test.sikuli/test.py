# The tests for r-project/rtools and rstudio/rstudio are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Test of `turbo run`.
wait("rstudio_window.png",60)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "RStudio.lnk"))

# Basic operations.
wait("rstudio_window.png",60)
App("RStudio").focus()
type(Key.UP, Key.WIN) # Maximize cmd window.
click("rstudio_window.png")
type('install.packages("tidyverse")' + Key.ENTER)
wait(10)

# There might be a prompt.
App("Question").focus()
if exists("install_from_sources.png"):
    click(Pattern("install_from_sources.png").targetOffset(44,31))
 
wait("rstudio_package_installed.png", 120)
click("rstudio_package_installed.png")
type("library(tidyverse)" + Key.ENTER)
wait("rstudio_package_imported.png",60)
type("1 + 2" + Key.ENTER)
wait("math.png")

# RTools.
setAutoWaitTimeout(20)
click(Pattern("menu_left.png").targetOffset(-16,-2))
wait(Pattern("project.png").targetOffset(-39,1))
click(Pattern("project.png").targetOffset(-42,0))
wait(Pattern("save_ws.png").targetOffset(-34,41))
click(Pattern("save_ws.png").targetOffset(-34,41))
wait("new_project.png",120)
click("new_project.png")
wait("new_package.png")
click("new_package.png")
click(Pattern("new_package_name.png").targetOffset(-34,5))
type("test")
click("new_package_create.png")
wait("project_template.png")
type("r", Key.ALT + Key.CTRL)
wait("project_run.png")
click("project_run.png")
type("install.packages(\"roxygen2\")")
type(Key.ENTER)
wait(10)
type("b", Key.CTRL + Key.SHIFT)
wait("project_build.png")

# Check "help".
setAutoWaitTimeout(20)
click(Pattern("menu_right.png").targetOffset(17,-2))
wait("r-help.png")
click(Pattern("r-help.png").targetOffset(-14,-2))
wait("help-window.png")
type(Key.F4, Key.ALT)
click(Pattern("save_ws.png").targetOffset(-34,41))
wait(10)

# Check if the session terminates.
util.check_running()
