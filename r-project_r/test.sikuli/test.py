script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import time
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
# Wait out the whole install in one go: the prompt is gone while R works and
# comes back when it is done, so "prompt vanished, then prompt returned" covers
# the download, the unpack, and the builds of the packages CRAN ships as sources
# only (tinytex, selectr) without the test having to know how long any stage
# takes.
#
# This replaces wait("r_console_pac_installed.png", 120) + click("console.png",90),
# which failed for two separate reasons. click()'s second argument is a modifier
# mask, not a timeout, so the prompt only ever got the 20 s setAutoWaitTimeout -
# about four seconds short of the 23.7-24.2 s the source builds need - and that
# is what killed runs 35654098667 and 35678863980, both with the console still
# on "installing the source packages 'tinytex', 'selectr'". And the image it
# waited on reads "The downloaded source packages are in" but matches the
# earlier "The downloaded binary packages are in" line at 0.87, so it returned
# mid-install; its own 120 s then proved too short as well, on a slower run that
# was still unpacking binaries when it expired (35780080379). Both were fixed
# budgets standing in for work of unknown length, so neither is kept.
#
# The vanish guard is what makes the single wait safe: the live prompt matches
# console.png at 0.75, so without it a wait starting before R got busy could
# return on the prompt the install has not consumed yet. Measured right after
# the mirror click the prompt is already gone (0.28-0.37), so in practice this
# returns at once - it is here for the run where it does not.
# PROBE ONLY - DO NOT MERGE. Probes the risk this rewrite introduces - that a
# single wait for the prompt could return on the prompt the install has not
# consumed yet - and the one the old code died on. Asserts, in order: the prompt
# is really gone once the install is under way (so the wait below cannot match
# early), and it then takes longer to come back than the 20 s the old click had.
# A passing probe run means the single wait is doing real waiting; either assert
# firing means the rewrite rests on something that is not true.
assert waitVanish("console.png", 60), "R never started installing - the prompt never went away"
assert exists("console.png", 0) is None, "PROBE: prompt still on screen after the install started - a single wait could match it"
_t0 = time.time()
click(wait("console.png", 900))
_elapsed = time.time() - _t0
Debug.user("PROBE: install ran %.1f s from the mirror click to the prompt coming back" % _elapsed)
assert _elapsed > 20, "PROBE: prompt came back in %.1f s - the old 20 s budget would have covered it" % _elapsed
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