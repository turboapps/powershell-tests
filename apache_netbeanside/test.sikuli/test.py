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
# SABOTAGE PROBE B (dead witness): same tight grace, but the busy image is
# click-me-button.png, which cannot be on screen until the file has been run.
# With nothing to see the wait must give up at about 8 s. The gap between this
# run's "gave up after N s" and probe A's is the dialog doing its job.
util.wait_while_busy(Pattern("hello-world-class.png").similar(0.85),
                     "click-me-button.png", timeout=600, grace=8)
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