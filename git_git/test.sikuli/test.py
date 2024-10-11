script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

repo_path = os.path.join(util.desktop, "Hello-World")

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("git-cmd-prompt.png")
type("git -help" + Key.ENTER)
wait("git-help.png")
type("exit")
type(Key.ENTER)
run("turbo stop test")

# Test headless trigger.
headlessCmd = os.path.join(script_path, os.pardir, "resources", "headless_cmd.bat")
repo = os.path.join(util.desktop, "Hello-World")
readme = os.path.join(repo, "README")
run("explorer " + headlessCmd)
wait(5)
assert(util.file_exists(readme, 10))

# Test Git GUI.
run("explorer " + os.path.join(util.start_menu, "Git", "Git GUI.lnk"))
wait("git-gui.png")
click("git-gui.png")
wait(3)
type("o", Key.CTRL)
wait(3)
type(repo + Key.ENTER)
wait("remote.png")
wait(3)
click("remote.png")
hover("fetch-from.png")
click("origin.png")
wait("fetch-success.png")
type(Key.F4, Key.ALT) # Close fetch window.
type(Key.F4, Key.ALT) # Close app.

wait(20) # wait for session to close.

# Check if the session terminates.
util.check_running()