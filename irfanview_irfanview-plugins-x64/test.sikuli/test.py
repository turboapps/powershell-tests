script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

save_path = os.path.join(util.desktop, "red fox.bmp")

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("irfanview-menu.png")
wait(3)

run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.desktop, "IrfanView 64.lnk"))
wait("irfanview-menu.png")
app_window = App().focus("IrfanView") # Activate and maximize the app window.
if app_window.isValid():
    type(Key.UP, Key.WIN)
wait(3)
type("o")
wait("file-open.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("fox-open.png")
# Test adobe plugin
click("image-menu.png")
hover("adobe-plugin-menu.png")
click("popart-plugin.png")
wait(Pattern("effect-boxes.png").targetOffset(2,-96))
click(Pattern("effect-boxes.png").targetOffset(3,-95))
type("a", Key.CTRL)
type("25")
click(Pattern("effect-boxes.png").targetOffset(3,-66))
type("a", Key.CTRL)
type("2")
click(Pattern("effect-boxes.png").targetOffset(2,-41))
type("a", Key.CTRL)
type("24")
click(Pattern("effect-boxes.png").targetOffset(3,-12))
type("a", Key.CTRL)
type("30")
click(Pattern("effect-boxes.png").targetOffset(3,15))
type("a", Key.CTRL)
type("0")
click(Pattern("effect-boxes.png").targetOffset(2,40))
type("a", Key.CTRL)
type("89")
click(Pattern("effect-boxes.png").targetOffset(2,70))
type("a", Key.CTRL)
type("163")
click(Pattern("effect-boxes.png").targetOffset(2,96))
type("a", Key.CTRL)
type("177")
click("ok-button.png")
wait("effect-applied.png")
wait(3)
type("s")
wait(3)
type(save_path)
wait(3)
type(Key.ENTER)
util.file_exists(save_path, 5)
type(Key.F4, Key.ALT) # close app
wait(10)

# Check if the session terminates.
util.check_running()