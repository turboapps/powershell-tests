script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# PROBE ONLY - DO NOT MERGE. Vacuity check on branch
# libreoffice-reopen-session-race.
#
# The fix has two protections: util.wait_app_quiet() settles the container
# before each launch, and util.reopen_in_new_window() additionally clears and
# retries the TURBO.NET "already running session" box if the race is still lost.
# A green run proves neither of them fired - the settle alone would produce the
# same green, and the retry path would be dead code nobody had exercised.
#
# So take the settle away and leave only the retry. Every launch now goes out
# while the sandbox is still tearing down, which is the state that produced
# App Tests run 35775188040.
#
# Reading the result: PASS plus "reopen_in_new_window: Turbo refused the launch"
# in the log means the retry path is live and rescues the race on its own. PASS
# with no such line means even a zero settle did not lose the race this time and
# the run says nothing. FAIL at a reopen means the retry is not enough by
# itself, which is an argument for the settle, not against it.
util.wait_app_quiet = lambda *args, **kwargs: True

# Every module below is exercised the same way: save a document, close the
# window, then reopen the saved file through its file association. Both halves
# of that are launches into the same Turbo container, and the close before them
# is fire-and-forget - Alt+F4 returns as soon as the window accepts it, while
# the sandbox behind it is still tearing down. A launch that lands in that gap
# opens nothing at all: the client logs
#
#   [INF] Retrying after launch in sandbox failed due to potential shutdown
#         race condition: Failed to start application in already running session
#   [FTL] Error: Failed to start application in already running session
#
# and leaves a TURBO.NET error box on the desktop, so the wait that follows
# spends its whole budget against a bare desktop and then reports the document
# image instead of the launch that never happened.
#
# App Tests run 35775188040 failed exactly there (line 73, test-db-open.png):
# step frame 028 is that error box, and the client log shows the client's own
# two internal retries, 5 s apart, both losing to a session that was still
# shutting down. The blind wait(5) this file used between the close and the
# relaunch is shorter than the teardown it is waiting for, and every one of the
# eleven launch sites had that or nothing at all.
#
# util.wait_app_quiet() waits for both halves to go quiet - the process off the
# task list AND the session out of `turbo sessions -l` - because measured on the
# pool VMs they settle in either order. util.reopen_in_new_window() does that
# and then also clears and retries the TURBO.NET box if the race still wins,
# which is the case a wait alone cannot cover.

# Test of `turbo run`.
wait("office-launched.png",90)
run("turbo stop test")
wait(10)
closeApp("Command Prompt")

# Test Office.
run("explorer " + os.path.join(util.start_menu, "LibreOffice", "LibreOffice.lnk"))
wait("office-launched.png",90)

# Test Writer.
click("writer-document.png")
if exists("didyouknow.png"):
    click("tip_show_startup.png")
    click("tip_ok.png")

# Test Help
type(Key.F1)
wait("read-help-online.png",30)
click("read-help-online.png")
wait("help-url.png",20)
util.close_app("Edge")

# Test Writer functions
wait("welcome.png",30)
click(Pattern("welcome.png").targetOffset(313,-1))
wait("blank-page.png",15)
click("blank-page.png")
paste("Test document")
type(Key.HOME, Key.SHIFT)
type("b", Key.CTRL)
type("i", Key.CTRL)
type("s", Key.CTRL)
wait("save-dialog.png",20)
save_path = os.path.join(util.desktop, "test-doc.odt")
paste(save_path)
wait(2)
type(Key.ENTER)
wait(5)
assert(util.file_exists(save_path, 5))
type(Key.F4, Key.ALT)
if not util.reopen_in_new_window(save_path, "test-doc-open.png", "soffice.bin"):
    raise FindFailed("the saved Writer document never reopened")
wait(3)
type(Key.F4, Key.ALT)
type("q", Key.CTRL)

# Test Base.
util.wait_app_quiet("soffice.bin")
run("explorer " + os.path.join(util.start_menu, "LibreOffice", "LibreOffice Base.lnk"))
wait("create-new-db.png")
click(Pattern("create-new-db.png").targetOffset(105,258))
wait("save-new-db.png")
save_path = os.path.join(util.desktop, "test-db.odb")
paste(save_path)
wait(2)
type(Key.ENTER)
assert(util.file_exists(save_path, 5))
wait(5)
type(Key.F4, Key.ALT)
if not util.reopen_in_new_window(save_path, "test-db-open.png", "soffice.bin"):
    raise FindFailed("the saved Base database never reopened")
wait(3)
type(Key.F4, Key.ALT)

# Test Calc.
util.wait_app_quiet("soffice.bin")
run("explorer " + os.path.join(util.start_menu, "LibreOffice", "LibreOffice Calc.lnk"))
wait("new-sheet.png")
click(Pattern("new-sheet.png").targetOffset(-74,-17))
wait(2)
type("2")
wait(2)
type(Key.TAB)
wait(2)
type("3")
wait(2)
type(Key.TAB)
wait(2)
type("=A1+B1")
wait(2)
type(Key.ENTER)
wait("sum-result.png")
type("s", Key.CTRL)
wait("save-new-sheet.png")
save_path = os.path.join(util.desktop, "test-ods.ods")
paste(save_path)
wait(2)
type(Key.ENTER)
wait(5)
assert(util.file_exists(save_path, 5))
type(Key.F4, Key.ALT)
if not util.reopen_in_new_window(save_path, "test-sheet-open.png", "soffice.bin"):
    raise FindFailed("the saved Calc sheet never reopened")
wait(3)
type(Key.F4, Key.ALT)

# Test Draw.
util.wait_app_quiet("soffice.bin")
run("explorer " + os.path.join(util.start_menu, "LibreOffice", "LibreOffice Draw.lnk"))
wait("shape-tool.png")
click("shape-tool.png")
click(Pattern("blank-drawing.png").targetOffset(-135,-108))
click(Pattern("blank-drawing.png").targetOffset(106,109))
wait("draw-shape.png")
type("s", Key.CTRL)
wait("save-new-drawing.png")
save_path = os.path.join(util.desktop, "test-odg.odg")
paste(save_path)
wait(2)
type(Key.ENTER)
wait(5)
type(Key.F4, Key.ALT)
if not util.reopen_in_new_window(save_path, "test-drawing-open.png", "soffice.bin"):
    raise FindFailed("the saved Draw drawing never reopened")
wait(3)
type(Key.F4, Key.ALT)

# Test Impress.
util.wait_app_quiet("soffice.bin")
run("explorer " + os.path.join(util.start_menu, "LibreOffice", "LibreOffice Impress.lnk"))
wait("new-presentation.png")
doubleClick("new-presentation.png")
paste("Test Presentation")
wait(2)
type("s", Key.CTRL)
wait("save-new-presentation.png")
save_path = os.path.join(util.desktop, "test-odp.odp")
paste(save_path)
wait(2)
type(Key.ENTER)
wait(5)
type(Key.F4, Key.ALT)
if not util.reopen_in_new_window(save_path, "test-presentation-open.png", "soffice.bin"):
    raise FindFailed("the saved Impress presentation never reopened")
wait(3)
type(Key.F4, Key.ALT)

# Test Math.
util.wait_app_quiet("soffice.bin")
run("explorer " + os.path.join(util.start_menu, "LibreOffice", "LibreOffice Math.lnk"))
wait("elements.png")
click(Pattern("elements.png").targetOffset(135,12))
click(Pattern("examples.png").targetOffset(-44,102))
click("example-formula.png")
wait("written-example.png")
type("s", Key.CTRL)
wait("save-new-formula.png")
save_path = os.path.join(util.desktop, "test-odf.odf")
paste(save_path)
wait(2)
type(Key.ENTER)
wait(5)
type(Key.F4, Key.ALT)
if not util.reopen_in_new_window(save_path, "test-formula-open.png", "soffice.bin"):
    raise FindFailed("the saved Math formula never reopened")
wait(3)
type(Key.F4, Key.ALT)

# Check if the session terminates.
wait(20)
util.check_running()