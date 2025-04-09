script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

pdf_path = os.path.join(script_path, os.pardir, "resources", "sample.pdf")
save_path =  os.path.join(util.desktop, "sample.pdf")

setAutoWaitTimeout(50)
util.pre_test()

# Test of `turbo run`.
wait("foxit_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Foxit PDF Reader", "Foxit PDF Reader.lnk"))
wait("foxit_window.png")
type("o", Key.CTRL)
click(Pattern("open_location.png").targetOffset(20,-4))
type(pdf_path)
type("o", Key.ALT)
wait("pdf_sample.png")

doubleClick(Pattern("pdf_sample.png").targetOffset(-182,-63))
doubleClick(Pattern("pdf_sample.png").targetOffset(-182,-63)) # Need to do this twice.
click("highlight-tool.png")
click(Pattern("text_sample_highlighted.png").similar(0.60).targetOffset(104,-10)) # Need to do this twice.
wait(Pattern("result_1.png").similar(0.60))
type("n", Key.CTRL + Key.SHIFT)
wait("comment_ready.png")
click(Pattern("result_1.png").similar(0.60).targetOffset(79,-16))
click(Pattern("comment_box.png").targetOffset(-1,10))
type("test" + Key.ESC)
wait(Pattern("result_2.png").similar(0.60))
type("s", Key.CTRL + Key.SHIFT)
wait("save_location.png")
type(save_path + Key.ENTER)
assert(util.file_exists(save_path, 5))
type(Key.F4, Key.ALT)
wait("sample-pdf-desktop.png")
rightClick("sample-pdf-desktop.png")
click("open-with.png")
click("choose-another-app.png")
click("open-with-foxit-reader.png")
click("always.png")
type(Key.ENTER)
wait(Pattern("foxit_opened.png").similar(0.60))
wait(5)
click("foxit_opened.png")
type(Key.F4, Key.ALT)
run("explorer " + save_path)
wait(Pattern("foxit_opened.png").similar(0.60))
wait(5)
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()
