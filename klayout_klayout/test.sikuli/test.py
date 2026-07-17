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
certOutFile = os.path.join(resources, "dirty.gds")
headlessCmd = "turbo run klayout --isolate=merge-user --working-dir=" + resources + " -- -b -r generate_dirty.py"
run(headlessCmd)
wait(5)
assert(util.file_exists(certOutFile, 10))


# Run GUI
run("explorer " + os.path.join(util.start_menu,"KLayout","KLayout (Default).lnk"))
wait("klayout-open.png",60)
type("o", Key.CTRL + Key.SHIFT)
wait(10)
paste(certOutFile)
wait(3)
type(Key.ENTER)
wait("dirty-open.png")
type("t", Key.ALT)
wait(3)
click("drc.png")
click("edit-drc.png")
wait(3)
click("close-tip.png")
click("import-drc.png")
wait(10)
drcfile = os.path.join(resources, "foundry.drc")
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