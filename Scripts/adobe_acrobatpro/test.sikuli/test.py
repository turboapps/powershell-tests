# Import the package "util" which contains common operations.
# More information: https://sikulix-2014.readthedocs.io/en/latest/scripting.html#importing-other-sikuli-scripts-reuse-code-and-images.
script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
common_path = os.path.join(script_path, os.pardir, os.pardir, "Common", "util.sikuli")
sys.path.append(common_path)
import util
reload(util)
addImagePath(common_path) # This is needed to include screenshots from "util".

# Set the default waiting time.
setAutoWaitTimeout(45)

# Operations before running individual test.
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# The location to save a file in the test.
save_location = os.path.join(util.desktop, "Special_Offers_Deck.pdf")

# `turbo run` should launch the app.
util.adobe_cc_login(username, password)
if exists("get-started.png"):
    type(Key.ESC)
wait("pdf_window.png")
run("turbo stop test")

# Launch the app by Start menu shortcut.
run("explorer " + os.path.join(util.start_menu, "Adobe Acrobat Pro.lnk"))

# Basic operations.
click("pdf_window.png")
type(Key.UP, Key.WIN)
wait(3)
wait("see-all-tools.png")
click("see-all-tools.png")
click("create-a-pdf.png")
wait("create-pdf-doc-icon.png")
click("create-pdf-doc-icon.png")
wait("create_file_location.png")
type(os.path.join(script_path, os.pardir, "resources", "get-started-acrobat-dc", "Special_Offers_Deck.pptx") + Key.ENTER)
wait(5)
wait("create-button.png")
click("create-button.png")
wait(60) # Generation of the pdf is very slow.
wait("point-2-point.png")
type("s", Key.CTRL + Key.SHIFT)
wait("save_file_location.png")
type(save_location + Key.ENTER)
wait(5)
type("p", Key.CTRL)
wait("blue-print-button.png")
type(Key.ESC)
wait(3)
type(Key.F4, Key.ALT)
run("explorer " + save_location)
wait("default_dialog.png")
click("default_acrobat_pro.png")
click("default_always.png")
click("default_ok.png")
wait("point-2-point.png")
type(Key.F4, Key.ALT)
wait(3)
run("explorer " + save_location)
wait("point-2-point.png")

# Check the "help" of the app.
type(Key.F1)
util.close_firewall_alert()
wait("help_url.png")
closeApp("Edge")
if exists("get-started.png"):
    type(Key.ESC)
type(Key.F4, Key.ALT)
wait(30)

# Check if the container terminates after closing the app.
util.check_running()