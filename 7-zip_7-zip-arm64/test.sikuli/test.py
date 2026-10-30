# The tests for 7-zip/7-zip, 7-zip/7-zip-x64 and 7-zip/7-zip-arm64 are the same.

# Import the package "util" which contains common operations.
# More information: https://sikulix-2014.readthedocs.io/en/latest/scripting.html#importing-other-sikuli-scripts-reuse-code-and-images.
script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
import shutil
addImagePath(include_path) # This is needed to include screenshots from "util".

# Set the default waiting time.
setAutoWaitTimeout(20)

# Operations before running individual test.
util.pre_test()

# Where the zip and unzip steps write. Remove leftovers from a previous run on
# the same machine first: with the archive and the extracted folder already
# present, 7-Zip's extract step raises a confirm-replace prompt the script does
# not expect, 7-Zip stays open behind it, and the run fails at check_running
# (seen on os-testvalidation, 2026-09-04). The file_exists asserts below would
# also pass on the stale files even if this run's zip or unzip had failed.
zip_folder = os.path.join(util.desktop, "7-zip-test")
if os.path.exists(zip_folder):
    shutil.rmtree(zip_folder)

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
# The Copy dialog that Extract opens zooms in from slightly smaller than its final
# size, so a match taken during the entrance animation is offset up and to the
# left of where OK comes to rest. In App Tests run 40982308340 (7-zip-arm64) the
# OK button was matched mid-zoom and clicked at L[1030,617] while the settled
# button is centred on L[1043,630] with its top edge at y=619: the click landed
# 2 px above the button, the dialog stayed open, nothing was extracted and the
# run failed at the file_exists assert below. Passing runs clicked L[1044,631]
# and L[1039,626] - the second one also caught the zoom, just not far enough out
# to miss. find_settled waits for the button to stop moving before clicking.
click(util.find_settled("extract_ok.png"))
# Fail at the cause, not at the file check, if the click still did not take.
if not waitVanish("extract_ok.png", 10):
    raise FindFailed("7-Zip Copy dialog is still open 10 s after clicking OK")
assert(util.file_exists(os.path.join(zip_folder, "util.sikuli"), 3))
type(Key.F4, Key.ALT)
type(Key.F4, Key.ALT) # Close the Explorer window.
wait(20)

# Check if the session terminates after closing the app.
util.check_running()