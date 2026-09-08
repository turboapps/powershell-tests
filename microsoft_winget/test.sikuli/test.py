script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test(no_min=True)

# Every command is pasted then submitted with Enter. Command Prompt on the
# Win11 24H2 pool VMs is hosted by Windows Terminal, which reads the clipboard
# asynchronously on Ctrl+V, so a bare paste() followed at once by Enter can run
# Enter on an empty prompt and leave the pasted command sitting unexecuted. That
# is how App Tests run 33849047386 died at wait("wingetcreate_help.png"): the
# screenshot shows a blank prompt line and then "wingetcreate help" with no
# output. Hold after each paste (util.paste_text) as the other console tests do.

# Test. Winget CMD window shows later so it is always on top.
wait("cmd.png")
util.paste_text("winget install wingetcreate", 3)
type(Key.ENTER)
wait("agreements.png")
util.paste_text("Y", 2)
type(Key.ENTER)
wait("package_installed.png")

# Check "help".
util.paste_text("winget --help", 2)
type(Key.ENTER)
wait("help.png")
util.paste_text("exit", 2)
type(Key.ENTER)
run("turbo stop test")
wait(20)

# Check if the session terminates.
util.check_stopped("test")

# Check if wingetcreate is installed successfully by winget.
wait(3)
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk")) # launch another command prompt
click("cmd1.png")
util.paste_text("wingetcreate help", 2)
type(Key.ENTER)
# If the banner is not up in 10 s the command most likely never ran; send it
# once more. Only the retry is gated here - the wait below stays the assertion.
if not exists("wingetcreate_help.png", 10):
    click("cmd1.png")
    util.paste_text("wingetcreate help", 2)
    type(Key.ENTER)
wait("wingetcreate_help.png")
util.paste_text("exit", 2)
type(Key.ENTER)