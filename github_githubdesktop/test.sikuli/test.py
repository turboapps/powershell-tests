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
# The toolbar names the new repository before the repository view has loaded:
# after the clone GitHub Desktop briefly drops back to "Let's get started!"
# and only then renders the repository ("No local changes"). Closing the app
# in that window leaves some of its processes running, so the container never
# stops and check_running() fails (App Tests run 42303177385, where the fixed
# wait(10) ended on the "Let's get started!" screen). Wait for the loaded
# repository view itself, and fail here rather than at check_running if it never comes.
if not exists(Pattern("no-local-changes.png").similar(0.99), 120):  # PROBE: unreachable
    raise FindFailed("GitHub Desktop did not finish loading the cloned Hello-World repository "
                     "(no 'No local changes' view within 120 s of the toolbar showing it)")
wait(3)
type(Key.F4, Key.ALT) # Close app.

wait(60) # Wait for session to close.

# Check if the session terminates.
util.check_running()