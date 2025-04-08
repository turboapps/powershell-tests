script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test(no_min=True)

# Test. Winget CMD window shows later so it is always on top.
wait("winget.png")
type("winget install wingetcreate" + Key.ENTER)
wait("agreements.png")
type("Y" + Key.ENTER)
wait("package_installed.png")

# Check "help".
type("winget --help" + Key.ENTER)
wait("help.png")
type("exit" + Key.ENTER)
run("turbo stop test")
wait(20)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))

# Check if wingetcreate is installed successfully by winget.
wait(3)
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk")) # launch another command prompt
click("cmd.png")
type("wingetcreate help" + Key.ENTER)
wait("wingetcreate_help.png")
type("exit" + Key.ENTER)