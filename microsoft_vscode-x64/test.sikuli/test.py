script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

save_path = os.path.join(util.desktop, "Untitled-1.py")

setAutoWaitTimeout(50)
util.pre_test()

# Test of `turbo run`.
wait("code_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Visual Studio Code", "Visual Studio Code.lnk"))
wait("code_window.png")

# Basic operations.
type("n", Key.CTRL)
type("def test(word):" + Key.ENTER)
type("    print(word)")
wait("install_extension.png")
wait(2)
click(Pattern("install_extension.png").targetOffset(59,26))
wait("install_complete.png", 240)
click("tab_unnamed.png")
type("s", Key.CTRL)
wait("save_location.png")
type(save_path + Key.ENTER)
wait(5)
type(Key.F4, Key.ALT)
wait(5)

run("explorer " + save_path)
wait("welcome-tab.png")
wait("untitled-tab-grey.png")
click("untitled-tab-grey.png")
wait("code.png")

# Check "help".
click(Pattern("menu.png").targetOffset(22,0))
click("menu_help.png")
click("menu_help_doc.png")
util.close_firewall_alert()
wait("help_url.png")
closeApp("Edge")
wait(10) # Wait for the complete close of the firewall alert.
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()