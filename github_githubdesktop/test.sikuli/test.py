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
wait("welcome.png")
wait(3)
type(Key.F4, Key.ALT) # Close app.
run("turbo stop test")

# Test basic app functions.
run("explorer " + os.path.join(util.desktop, "GitHub Desktop.lnk"))
wait("welcome.png")
wait(3)
click("skip-link.png")
click(Pattern("configure.png").targetOffset(-84,-23))
type("test"+ Key.TAB)
type("test@git.com" + Key.ENTER)
wait("clone-repo.png")
click("clone-repo.png")
click("url.png")
type("https://github.com/octocat/Hello-World" + Key.TAB)
type(repo_path + Key.ENTER)
wait("current-repo.png")
wait(10)
type(Key.F4, Key.ALT) # Close app.

wait(60) # Wait for session to close.

# Check if the session terminates.
util.check_running()