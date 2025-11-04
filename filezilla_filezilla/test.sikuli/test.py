# The tests for filezilla/filezilla and filezilla/filezilla-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Test of `turbo run`.
wait("filezilla_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "FileZilla FTP Client", "FileZilla.lnk"))
click("filezilla_window.png")

# Basic operations.
paste("test.rebex.net")
type(Key.TAB)
wait(3)
paste("demo")
type(Key.TAB)
wait(3)
paste("password")
type(Key.ENTER)
wait("cert-ok.png")
click("cert-ok.png")
wait("remote-file.png",60)

# Check "help".
click(Pattern("menu.png").targetOffset(59,0))
click("menu_help.png")
wait("help_url.png")
closeApp("Edge")
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()
