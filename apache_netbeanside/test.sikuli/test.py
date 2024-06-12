script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Test of `turbo run`.
wait("logo.png",30)
run("turbo stop test")


# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.desktop, "Apache NetBeans IDE"))

# Basic operations.
wait("logo.png",30)
click("file-menu.png")
click("open-file.png")
type(os.path.join(script_path, os.pardir, "resources", "HelloWorld.java") + Key.ENTER)
wait("hello-world-class.png",40)
wait(20)
click("Run-menu.png")
click("run-file.png")
wait("click-me-button.png")
click("click-me-button.png")
type(Key.ENTER)
type(Key.F4, Key.ALT)
click("file-menu.png")
click("exit.png")
wait(20)

# Check if the session terminates.
util.check_running()