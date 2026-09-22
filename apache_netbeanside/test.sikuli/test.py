script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("logo.png", 120)
run("turbo stop test")


# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.desktop, "Apache NetBeans IDE"))

# Basic operations.
wait("logo.png", 120)
click("file-menu.png")
click(Pattern("open-file.png").targetOffset(-22,12))
wait("file-open.png")
paste(os.path.join(script_path, os.pardir, "resources", "HelloWorld.java"))
wait(2)
type(Key.ENTER)
# Opening the first Java file puts up a modal "Opening File HelloWorld.java"
# progress dialog while NetBeans activates Java SE and starts its modules,
# so wait for the editor for as long as that dialog says it is still working.
# SABOTAGE PROBE A (live witness): grace cut to 8 s. If opening-file.png is
# really being matched the wait survives for as long as the dialog is up and
# only dies in the blank-pane gap after it closes, so the "gave up after N s"
# in the FindFailed must be far greater than 8. Expected to FAIL, late.
util.wait_while_busy(Pattern("hello-world-class.png").similar(0.85),
                     "opening-file.png", timeout=600, grace=8)
wait(20)
click("Run-menu.png")
click("run-file.png")
wait("click-me-button.png")
click("click-me-button.png")
type(Key.ENTER)
wait(5)
click("file-menu.png")
click("exit.png")
wait(20)

# Check if the session terminates.
util.check_running()