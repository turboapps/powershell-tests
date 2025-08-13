# The tests for microsoft/office-o365business-x64 and microsoft/office-o365proplus-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(60)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run` and log in.
wait("sign-in.png",120)
type(Key.F4, Key.ALT)
click("office-sign-in.png")
wait("sign-in-username.png")
click(Pattern("sign-in-username.png").targetOffset(75,2))
type(username + Key.ENTER)
wait("office_signin_password.png")
type(password + Key.ENTER)
click("office-all-apps.png")
if exists("office_signin_wrong.png"):
    type(Key.ENTER)
else:
    wait("office_signin_all_set.png")
    type(Key.ENTER)
run("turbo stop test")

# OneNote.
run("explorer " + os.path.join(util.start_menu, "OneNote.lnk"))
click("sign-in.png")
if exists("sign-in-username.png"):
    click(Pattern("sign-in-username.png").targetOffset(75,2))
    type(username + Key.ENTER)
click("office-sign-in.png")
wait("sign-in-username.png")
click(Pattern("sign-in-username.png").targetOffset(75,2))
type(username + Key.ENTER)
wait("onenote-launched.png")
if exists("notebooks-cancel.png",30):
    click("notebooks-cancel.png")
wait("new-section.png")
click("new-section.png")
wait(5)
type("Test" + Key.TAB)
type("first line" + Key.ENTER)
type("second line" + Key.ENTER)
type("third line")
type(Key.HOME, Key.CTRL) # Move the cursor to the start of the document.
type(Key.DOWN, Key.SHIFT) # Select the whole line.
type("b", Key.CTRL) # Bold text.
type(Key.RIGHT) # Move the cursor to the next line.
type(Key.DOWN, Key.SHIFT)
type("i", Key.CTRL) # Italic text.
type(Key.RIGHT)
type(Key.DOWN, Key.SHIFT)
type("u", Key.CTRL) # Underline text.
type(Key.RIGHT)
wait("onenote_result_1.png")

click(Pattern("onenote_menu.png").targetOffset(-88,1))
click("onenote_table.png")
wait(2)
click(Pattern("onenote_table_menu.png").targetOffset(-24,-12))
wait("onenote_table_insert.png")
type(Key.ENTER)
wait("onenote_result_2.png")

click(Pattern("onenote_menu.png").targetOffset(-88,1))
click("onenote_pictures.png")
wait(2)
click(Pattern("onenote_pictures_menu.png").targetOffset(-9,-27))
wait("onenote_file_name.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("onenote_result_3.png")

click(Pattern("onenote_menu.png").targetOffset(-88,1))
click("onenote_file.png")
wait("onenote_file_name.png")
type(os.path.join(script_path, os.pardir, "resources", "csv.csv") + Key.ENTER)
wait("onenote_result_4.png")

type("p", Key.CTRL)
wait("onenote_print.png")
type(Key.ESC)
wait("onenote_result_4.png")
rightClick("quick-notes-notebook.png")
click("delete-note.png")
click("yes-delete.png")

type(Key.F1)
wait("onenote_help.png")
wait(20) # Wait for syncing.

type(Key.F4, Key.ALT)
os.system('cmd /c taskkill /f /im "smartscreen.exe" /t')
wait(20)

# Check if the session terminates.
util.check_running()