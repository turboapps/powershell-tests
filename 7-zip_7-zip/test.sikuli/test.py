# The tests for 7-zip/7-zip and 7-zip/7-zip-x64 are the same.

# Import the package "util" which contains common operations.
# More information: https://sikulix-2014.readthedocs.io/en/latest/scripting.html#importing-other-sikuli-scripts-reuse-code-and-images.
script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path) # This is needed to include screenshots from "util".

# Set the default waiting time.
setAutoWaitTimeout(20)

# Operations before running individual test.
util.pre_test()

# `turbo run` should launch the app.
wait("zip_add.png")
run("turbo stop test")

# Launch the app by Start menu shortcut.
run("explorer " + os.path.join(util.start_menu, "7-Zip", "7-Zip File Manager.lnk"))
wait("zip_add.png")

# Activate and maximize the app window.
app_window = App().focus("7-Zip")

# Check the "help" of the app.
type(Key.F1)
click(Pattern("help.png").targetOffset(245,-23))

# Basic operations: zip.
click(Pattern("address_bar.png").targetOffset(20,0))
paste(os.path.join(script_path, os.pardir, os.pardir, "!include"))
type(Key.ENTER)
click("folder.png")
wait(3)
click("zip_add.png")
wait(3)
click(Pattern("format.png").targetOffset(56,-3))
wait(3)
click(Pattern("format_selection.png").targetOffset(-57,28))
wait(3)
click("zip_location.png")
zip_folder = os.path.join(util.desktop, "7-zip-test")
zip_path = os.path.join(zip_folder, "util.sikuli.zip")
paste(zip_path)
type(Key.ENTER)
assert(util.file_exists(zip_path, 3))
type(Key.F4, Key.ALT)

# Basic operations: unzip.
run("explorer " + zip_folder)
rightClick("folder_zipped.png")
click("open_with.png")
click("open_with_7zip.png")
wait("zip_extract.png")
wait(2)
click("zip_extract.png")
click("extract_ok.png")
assert(util.file_exists(os.path.join(zip_folder, "util.sikuli"), 3))
type(Key.F4, Key.ALT)
type(Key.F4, Key.ALT) # Close the Explorer window.
wait(20)

# Check if the session terminates after closing the app.
util.check_running()