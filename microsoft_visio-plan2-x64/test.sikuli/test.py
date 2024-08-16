script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "test.vsdx")

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
click(Pattern("office_signin.png").targetOffset(-116,135))
wait("office_signin_email.png")
type(username + Key.ENTER)
wait("office_signin_password.png")
type(password + Key.ENTER)
wait("office_signin_all_apps.png")
type(Key.ENTER)
if exists("office_signin_wrong.png"):
    type(Key.ENTER)
else:
    wait("office_signin_all_set.png")
    type(Key.ENTER)
wait("basic_diagram.png")
type(Key.F4, Key.ALT)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Visio.lnk"))
if exists("office_signin.png"):
    click(Pattern("office_signin.png").targetOffset(-116,135))
    wait("office_signin_email.png")
    type(username + Key.ENTER)

# Basic operations.
click("basic_diagram.png")
click(Pattern("basic_diagram_create.png").targetOffset(-85,87))
wait("tools.png")
wait(2)
click(Pattern("shapes.png").targetOffset(-68,-50))
dragDrop(Pattern("rectangle.png").targetOffset(-341,115), Pattern("rectangle.png").targetOffset(319,-16))
wait("result_1.png")
dragDrop(Pattern("square.png").targetOffset(-380,111), Pattern("square.png").targetOffset(404,-20))
wait("result_2.png")
type("s", Key.CTRL)
click(Pattern("save.png").targetOffset(-4,-39))
click(Pattern("save_location_1.png").targetOffset(-10,48))
wait("save_location_2.png")
type(save_location + Key.ENTER)
assert(util.file_exists(save_location, 5))

type(Key.F4, Key.ALT)
wait(20)
run("explorer " + save_location)
wait("result_3.png")

type("p", Key.CTRL)
wait("print_window.png")
type(Key.ESC)
wait("result_3.png")

# Check "help".
type(Key.F1)
wait("help_window.png")
type(Key.F4, Key.ALT)
wait(45)

# Check if the session terminates.
util.check_running()