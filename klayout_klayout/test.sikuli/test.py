# The tests for klayout and klayout-x64 are the same

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)
resources = os.path.join(script_path, os.pardir, "resources")

setAutoWaitTimeout(30)
util.pre_test()

# Test.
wait("klayout-open.png",60)
wait(5)
closeApp("KLayout")
wait(5)
run("turbo stop test")
wait(10)


# Run headless to create dirty
certOutFile = os.path.join(util.desktop, "dirty.gds")
genScript = os.path.join(resources, "generate_dirty.py")
headlessCmd = "turbo run klayout --isolate=merge-user --working-dir=" + util.desktop + " -- -b -r " + genScript
run(headlessCmd)
wait(5)
assert(util.file_exists(certOutFile, 10))


# Run GUI
run("explorer " + os.path.join(util.start_menu,"KLayout","KLayout (Default).lnk"))
wait("klayout-open.png",60)
# The main window is not reliably focused once the empty canvas appears on the
# CI pool VMs, so Ctrl+Shift+O is swallowed, the Open dialog never opens and the
# path is pasted into nothing: the layout stays unloaded and the test dies five
# lines down at wait("dirty-open.png") with the app still on its "Use File/Open
# to open a layout" splash (App Tests run 33849047386 on w11-19, same image
# 0.30.12, client and VM that passed on every other pool VM). Activate the window
# first, then wait for the dialog rather than sleeping blind, and press the hotkey
# again if it did not open. The dialog check only gates the retry - the layout
# itself is still the assertion, so this cannot fail a run on its own.
# Match the dialog title crisply: at SikuliX's default 0.7 a half-drawn (or
# half-closed) dialog matches, and the path would be pasted into a box that is
# not ready. A CI run measured 100% on the settled dialog and 74% on a fading
# one, so 0.9 separates them.
open_dialog = Pattern("open-dialog.png").similar(0.9)
util.activate_app_window("KLayout", 10)
type("o", Key.CTRL + Key.SHIFT)
if not exists(open_dialog, 10):
    util.activate_app_window("KLayout", 10)
    type("o", Key.CTRL + Key.SHIFT)
    exists(open_dialog, 15)
wait(1)
paste(certOutFile)
wait(3)
type(Key.ENTER)
wait("dirty-open.png")
# The Tools menu is the same swallowed-hotkey risk, right after the layout loads.
util.activate_app_window("KLayout", 10)
type("t", Key.ALT)
if not exists("drc.png", 5):
    type(Key.ESC)
    wait(1)
    util.activate_app_window("KLayout", 10)
    type("t", Key.ALT)
click("drc.png")
# The DRC submenu closes again as soon as anything takes focus, and the run
# then dies on the submenu item rather than on the menu itself: reopen the
# menu and click through again.
if not exists("edit-drc.png", 5):
    type(Key.ESC)
    wait(1)
    util.activate_app_window("KLayout", 10)
    type("t", Key.ALT)
    click("drc.png")
click("edit-drc.png")
wait(3)
click("close-tip.png")
drcfile = os.path.join(resources, "foundry.drc")
# Importing the rule file was the same blind paste as opening the layout: the
# path went in a fixed 10 s after the click, into whatever had focus. When the
# dialog is late or loses focus the path never lands, the dialog sits there with
# an empty File name box and the run dies at doubleClick("foundry.png"). Wait
# for the dialog and focus it before pasting.
import_dialog = Pattern("import-dialog.png").similar(0.9)
click("import-drc.png")
exists(import_dialog, 20)
util.activate_app_window("Import Macro File", 5)
wait(1)
paste(drcfile)
wait(3)
type(Key.ENTER)
# Retry only when the macro really did not arrive AND the dialog is still
# there. Checking the outcome first keeps the healthy run free of stray input:
# a dialog caught mid-close used to trigger a pointless second paste into the
# window behind it.
if not exists("foundry.png", 10) and exists(import_dialog, 2):
    util.activate_app_window("Import Macro File", 5)
    wait(1)
    paste(drcfile)
    wait(3)
    type(Key.ENTER)
doubleClick("foundry.png")
click("play-drc.png")
click("yes-save.png")
wait("test-result.png")
wait(5)
click("close-tip.png")
closeApp("Macro Development")
closeApp("KLayout")

# Check if the session terminates.
assert("test" not in run("turbo sessions"))