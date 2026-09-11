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
wait("rstudio_window.png",120)
click("whatsnew-close.png")
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
# Set the name and create the package, then check the outcome rather than
# trusting it.
#
# The field has to be located through util.find_settled: the click on
# new_package.png slides the Create R Package page in, and a find that catches
# it mid-slide clicks where the field no longer is (see find_settled).
#
# That is not the only way "test" can fail to land, though, and none of them
# announce themselves - a lost keystroke leaves the same empty field. What the
# wizard does say is that the name is empty, in an "Invalid package name ''"
# box raised by Create Project; in App Tests runs 34423171312 and 34295135821
# that box sat unread over the wizard while the test spent 20 s waiting for a
# project template that was never going to be created. OK is the box's default
# button and dismissing it leaves the wizard on the same page, so the whole
# name-and-create step can simply be redone. Ctrl+A before typing clears
# anything a stray keystroke already put in the field.
for attempt in range(3):
    click(util.find_settled("new_package_name.png").getCenter().offset(41, 7))
    type("a", Key.CTRL)
    type("test")
    click("new_package_create.png")
    if exists("project_template.png", 60):
        break
    # Only a rejected name leaves the wizard up, so if it has gone the project
    # is being created and this wait was simply short - creating the project
    # and restarting the R session into it took 20-25 s on the slow pool VM of
    # probe run 34544390344. Retrying on that would type into the new project
    # and then hunt for a wizard that no longer exists, which is how the first
    # cut of this loop turned a slow success into a 30 s FindFailed.
    if not exists("new_package_create.png", 0):
        Debug.user("new package: the wizard has closed, the project is still being created")
        break
    Debug.user("new package: the name did not take on attempt %d of 3" % (attempt + 1))
    type(Key.ENTER)
    wait(1)
else:
    raise FindFailed("the New Project Wizard never created the 'test' package")
wait("project_template.png", 120)
type("r", Key.ALT + Key.CTRL)
wait("project_run.png")
click("project_run.png")
type("install.packages(\"roxygen2\")")
type(Key.ENTER)
wait(10)
type("b", Key.CTRL + Key.SHIFT)
# project_build.png is the "> library(test)" the console echoes only after
# Ctrl+Shift+B has run roxygen2, built and installed the package with
# Rcmd.exe INSTALL, and restarted the R session - a chain that does not fit
# the ambient 20 s. In App Tests run 34423192441 the build had reached
# "* DONE (test)" and "Restarting R session..." when the wait gave up, and the
# harness screenshot taken seconds later shows "> library(test)" and
# "Attaching package: 'test'": the package built correctly and the test threw
# the run away for want of a few more seconds. The install.packages() above it
# keeps its blind wait: RStudio queues the Ctrl+Shift+B when the console is
# still busy - that is what happened in that run, and the build ran in full -
# so a slow install now only spends part of this budget.
wait("project_build.png", 180)

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
