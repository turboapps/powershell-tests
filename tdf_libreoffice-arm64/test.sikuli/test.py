script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# PROBE ONLY - DO NOT MERGE. Sabotage of the fix on branch
# libreoffice-reopen-session-race.
#
# The fix's claim is that the Base reopen at the old line 73 races the container
# teardown that Alt+F4 started, and that the blind wait(5) before it is what
# lets the race be lost. This branch makes that state happen on purpose instead
# of waiting for it: the settle before the Base reopen is removed entirely, so
# the launch goes out while the sandbox is certainly still shutting down.
#
# A trailing assert names what was actually on screen, so a failure here reads
# as the TURBO.NET box rather than as a missing document image. If this branch
# fails at the Base reopen with turbo-session-error.png on screen, the
# mechanism is the one the fix addresses; if it passes every time, the fix is
# aimed at the wrong thing and the wait(5) was not the lever.
#
# Everything after the Base reopen is left exactly as main has it.

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
wait(5)
run("explorer " + save_path)
wait("test-doc-open.png",60)
wait(3)
type(Key.F4, Key.ALT)
type("q", Key.CTRL)

# Test Base.
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
run("explorer " + save_path)   # PROBE: no settle at all - maximise the race
if not exists("test-db-open.png", 60):
    saw_error = exists("turbo-session-error.png", 0) is not None
    Debug.user("PROBE: the Base reopen did not open the database; "
               "turbo-session-error.png on screen: %s" % saw_error)
    assert not saw_error, ("PROBE REPRODUCED: the launch lost the teardown race "
                           "and Turbo refused it with the already-running-session error")
    raise FindFailed("PROBE: test-db-open.png never appeared, and the Turbo "
                     "error box was not the reason")
wait(3)
type(Key.F4, Key.ALT)

# Test Calc.
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
wait(5)
run("explorer " + save_path)
wait("test-sheet-open.png")
wait(3)
type(Key.F4, Key.ALT)

# Test Draw.
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
wait(5)
run("explorer " + save_path)
wait("test-drawing-open.png")
wait(3)
type(Key.F4, Key.ALT)

# Test Impress.
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
wait(5)
run("explorer " + save_path)
wait("test-presentation-open.png")
wait(3)
type(Key.F4, Key.ALT)

# Test Math.
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
wait(5)
run("explorer " + save_path)
wait("test-formula-open.png")
wait(3)
type(Key.F4, Key.ALT)

# Check if the session terminates.
wait(20)
util.check_running()