script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# Test of `turbo run`.
wait("office-launched.png")
run("turbo stop test")
wait(10)

# Test help.
run("explorer " + os.path.join(util.start_menu, "LibreOffice", "LibreOffice Writer.lnk"))
wait("help-menu.png")
type(Key.F1)
wait("read-help-online.png")
click("read-help-online.png")
util.close_firewall_alert()
wait("help-url.png")
closeApp("Edge")
type(Key.F4, Key.ALT)
wait(5)

# Test Office.
run("explorer " + os.path.join(util.start_menu, "LibreOffice", "LibreOffice.lnk"))
wait("office-launched.png")

# Test Writer.
click("writer-document.png")
wait("blank-page.png")
type("Test document")
type(Key.HOME, Key.SHIFT)
type("b", Key.CTRL)
type("i", Key.CTRL)
type("s", Key.CTRL)
wait("save-dialog.png")
save_path = os.path.join(util.desktop, "test-doc.odt")
type(save_path + Key.ENTER)
wait(5)
assert(util.file_exists(save_path, 5))
type(Key.F4, Key.ALT)
wait(5)
run("explorer " + save_path)
wait("test-doc-open.png")
wait(3)
type(Key.F4, Key.ALT)

# Test Base.
run("explorer " + os.path.join(util.start_menu, "LibreOffice", "LibreOffice Base.lnk"))
wait("create-new-db.png")
click(Pattern("create-new-db.png").targetOffset(105,258))
wait("save-new-db.png")
save_path = os.path.join(util.desktop, "test-db.odb")
type(save_path + Key.ENTER)
assert(util.file_exists(save_path, 5))
wait(5)
type(Key.F4, Key.ALT)
wait(5)
run("explorer " + save_path)
wait("test-db-open.png")
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
type(save_path + Key.ENTER)
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
type(save_path + Key.ENTER)
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
type("Test Presentation")
wait(2)
type(Key.F5)
wait("view-presentation.png")
type(Key.ESC)
type("s", Key.CTRL)
wait("save-new-presentation.png")
save_path = os.path.join(util.desktop, "test-odp.odp")
type(save_path + Key.ENTER)
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
type(save_path + Key.ENTER)
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