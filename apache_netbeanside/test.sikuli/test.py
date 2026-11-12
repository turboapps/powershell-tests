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
# Apache's own installer (NetBeans <= 25) named the shortcut "Apache NetBeans IDE <ver>".
# From NetBeans 26 the image is built from the Friends of Apache NetBeans installer,
# which names it "Apache NetBeans <ver>", so match the common prefix. The desktop
# shortcut is an Inno Setup task (on by default); fall back to the Start Menu one,
# and list what is installed if neither is there.
shortcut = None
for folder in (util.desktop, util.start_menu):
    if os.path.exists(folder):
        matches = sorted(f for f in os.listdir(folder)
                         if f.startswith("Apache NetBeans") and f.lower().endswith(".lnk"))
        if matches:
            shortcut = os.path.join(folder, matches[0])
            break
if shortcut is None:
    raise AssertionError("No Apache NetBeans shortcut found.\nDesktop:\n  %s\nStart Menu:\n  %s"
        % ("\n  ".join(util.list_shortcuts(util.desktop)) or "(nothing)",
           "\n  ".join(util.list_shortcuts(util.start_menu)) or "(nothing)"))
run("explorer " + shortcut)

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
util.wait_while_busy(Pattern("hello-world-class.png").similar(0.85),
                     "opening-file.png", timeout=600)
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