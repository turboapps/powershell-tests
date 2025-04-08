script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(90)
save_path = os.path.join(util.desktop, "test.icml")

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait(120)
util.adobe_cc_login(username, password)
wait("incopy_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe InCopy"))
wait(120)

# Basic operations.
wait("incopy_window.png")
type("n", Key.CTRL)
wait("new_document.png")
type(Key.ENTER)
wait("new_file.png")
type("test")
click(Pattern("new_file.png").targetOffset(61,12))
wait("layout_view.png")
type("s", Key.CTRL)
wait("save_location.png")
type(save_path + Key.ENTER)
wait("user.png")
type("turbo" + Key.ENTER)
assert(util.file_exists(save_path, 5))
type("q", Key.CTRL)

wait(30)
run("explorer " + save_path)
wait(120)
wait(Pattern("untitled-1.png").similar(0.85))

# Check "help".
type(Key.F1)
wait("help_url.png")
closeApp("Edge")
wait(10)
type("q", Key.CTRL)
wait(10)

# Check if the session terminates.
util.check_running()