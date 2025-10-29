script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test(no_min=True)

# Minimize the sikulix console
if exists("sikulix-console.png",15):
    click("sikulix-console.png")
    wait(2)
    type(Key.DOWN, Key.WIN)

# Test. Winget CMD window shows later so it is always on top.
wait("winget.png")
paste("winget install wingetcreate")
wait(3)
type(Key.ENTER)
wait("agreements.png")
paste("Y")
type(Key.ENTER)
wait("package_installed.png")

# Check "help".
paste("winget --help")
type(Key.ENTER)
wait("help.png")
paste("exit")
type(Key.ENTER)
run("turbo stop test")
wait(20)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))

# Check if wingetcreate is installed successfully by winget.
wait(3)
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk")) # launch another command prompt
click("cmd.png")
paste("wingetcreate help")
type(Key.ENTER)
wait("wingetcreate_help.png")
paste("exit")
type(Key.ENTER)