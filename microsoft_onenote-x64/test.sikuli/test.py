# The tests for microsoft/office-o365business-x64 and microsoft/office-o365proplus-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run` and log in.
wait("sign-in.png",120)
type(Key.F4, Key.ALT)
click("office-sign-in.png")
wait("sign-in-username.png",20)
click(Pattern("sign-in-username.png").targetOffset(75,2))
paste(username)
wait(2)
type(Key.ENTER)
wait("office_signin_password.png",20)
paste(password)
wait(2)
type(Key.ENTER)
if exists("office-all-apps.png",10):
    click("office-all-apps.png")
if exists("device-reg-done.png",15):
    click("device-reg-done.png")
if exists("office_signin_wrong.png",10):
    type(Key.ENTER)
if exists("office_signin_all_set.png",10):
    type(Key.ENTER)
if exists("privacy-close.png",10):
    click("privacy-close.png")
run("turbo stop test")

# OneNote.
run("explorer " + os.path.join(util.start_menu, "OneNote.lnk"))
if exists("sign-in.png",15):
    click("sign-in.png")
if exists("sign-in-username.png",10):
    click("sign-in-username.png")
    wait(3)
    click(Pattern("sign-in-username.png").targetOffset(77,0))
    paste(username)
    wait(2)
    type(Key.ENTER)
if exists("sign-in-email-address.png",10):
    click("sign-in-email-address.png")
    wait(3)
    click(Pattern("sign-in-email-address.png").targetOffset(47,2))
    paste(username)
    wait(2)
    type(Key.ENTER)
if exists("continue.png",10):
    click("continue.png")
if exists("office-sign-in.png",10):
    click("office-sign-in.png")
    wait("sign-in-username.png",10)
    click(Pattern("sign-in-username.png").targetOffset(75,2))
    paste(username)
    wait(2)
    type(Key.ENTER)
if exists("office_signin_password.png",10):
    paste(password)
    wait(2)
    type(Key.ENTER)
if exists("privacy-close.png",10):
    click("privacy-close.png")
wait("onenote-launched.png",30)
if exists("notebooks-cancel.png",30):
    click("notebooks-cancel.png")
wait("new-section.png",20)
click("new-section.png")
wait(5)
paste("Test")
wait(2)
type(Key.TAB)
paste("Test")
wait(2)
type(Key.TAB)
paste("first line")
wait(2)
type(Key.ENTER)
paste("second line")
wait(2)
type(Key.ENTER)
paste("third line")
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
wait("onenote_result_1.png",20)

click(Pattern("onenote_menu.png").targetOffset(-88,1))
click("onenote_table.png")
wait(2)
click(Pattern("onenote_table_menu.png").targetOffset(-24,-12))
wait("onenote_table_insert.png",10)
type(Key.ENTER)
wait("onenote_result_2.png",10)

click(Pattern("onenote_menu.png").targetOffset(-88,1))
click("onenote_pictures.png")
wait(2)
click(Pattern("onenote_pictures_menu.png").targetOffset(-9,-27))
wait("onenote_file_name.png",20)
paste(os.path.join(script_path, os.pardir, "resources", "red fox.jpg"))
wait(2)
type(Key.ENTER)
wait("onenote_result_3.png",20)

click(Pattern("onenote_menu.png").targetOffset(-88,1))
click("onenote_file.png")
wait("onenote_file_name.png",10)
paste(os.path.join(script_path, os.pardir, "resources", "csv.csv"))
wait(2)
type(Key.ENTER)
wait("onenote_result_4.png",20)

type("p", Key.CTRL)
wait("onenote_print.png",20)
type(Key.ESC)
wait("onenote_result_4.png",10)
if exists("quick-notes-notebook.png",10):
    rightClick("quick-notes-notebook.png")
    click("delete-note.png")
    click("yes-delete.png")
if exists("new-section-1.png",10):
    rightClick("new-section-1.png")
    click("delete-note.png")
    click("yes-delete.png")
type(Key.F1)
wait("onenote_help.png",20)
wait(20) # Wait for syncing.

type(Key.F4, Key.ALT)
os.system('cmd /c taskkill /f /im "smartscreen.exe" /t')
wait(20)

# Check if the session terminates.
util.check_running()