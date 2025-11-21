script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "test.mpp")

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
click(Pattern("office_signin.png").targetOffset(-113,128))
wait("office_signin_email.png")
paste(username)
wait(2)
type(Key.ENTER)
wait("office_signin_password.png")
paste(password)
wait(2)
type(Key.ENTER)
if exists("yes-all-apps.png",10):
    click("yes-all-apps.png")
if exists("device-reg-done.png",15):
    click("device-reg-done.png")
if exists("office_signin_wrong.png",10):
    type(Key.ENTER)
if exists("office_signin_all_set.png",10):
    type(Key.ENTER)
if exists("privacy-close.png",10):
    click("privacy-close.png")
wait(5)
wait("blank_project.png")
type(Key.F4, Key.ALT)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Project.lnk"))
if exists("office_signin.png"):
    click(Pattern("office_signin.png").targetOffset(-113,128))
    wait("office_signin_email.png")
    type(username + Key.ENTER)
if exists("office_signin_password.png",10):
    type(password + Key.ENTER)
if exists("privacy-close.png",10):
    click("privacy-close.png")
# Basic operations.
click("blank_project.png")
click(Pattern("project_window.png").targetOffset(63,5))
type("task1" + Key.ENTER + Key.UP)
type("a", Key.CTRL + Key.SHIFT)
wait("result_1.png")
type(Key.ENTER)
type("task2" + Key.ENTER + Key.UP)
type("a", Key.CTRL + Key.SHIFT)
wait("result_2.png")
type(Key.ENTER)
type("task3" + Key.ENTER + Key.UP)
type("a", Key.CTRL + Key.SHIFT)
click("result_3.png")
type(Key.RIGHT, Key.ALT + Key.SHIFT)
wait("result_4.png")

type("s", Key.CTRL)
click(Pattern("save_location_1.png").targetOffset(-30,42))
wait("save_location_2.png")
paste(save_location)
wait(2)
type(Key.ENTER)
assert(util.file_exists(save_location, 5))
type("w", Key.CTRL)
run("explorer " + save_location)
wait("result_4.png")

type("p", Key.CTRL)
wait("print_window.png")
type(Key.ESC)
wait("result_4.png")

# Check "help".
type(Key.F1)
wait("help_window.png")
type(Key.F4, Key.ALT)
os.system('cmd /c taskkill /f /im "smartscreen.exe" /t')
wait(45)

# Check if the session terminates.
util.check_running()