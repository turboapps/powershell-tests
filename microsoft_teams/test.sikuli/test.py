script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("teams_window.png")
run("turbo stop test")
wait(20)

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Microsoft Teams"))
wait("teams_window.png")

# URL handler.
# Workaround for escaping % sign.
run('explorer "https://turbo.net"')
wait("url.png")

# Activate and maximize the app window.
app_window = App().focus("Edge")
if app_window.isValid():
    type(Key.UP, Key.WIN)

type("l", Key.CTRL)
type("https://teams.microsoft.com/l/meetup-join/19%3ameeting_MWE2YzViZDItM2NjNi00MzJjLWI3YjAtMDlkYmRmNGYzN2Jl%40thread.v2/0?context=%7b%22Tid%22%3a%2247c7235b-376c-4598-a69c-3614fd25ceed%22%2c%22Oid%22%3a%22db4f93b1-ee86-47b7-993e-f1e338809450%22%7d" + Key.ENTER)
click(Pattern("url_handler.png").targetOffset(129,47))
closeApp("Edge")
click(Pattern("meeting.png").targetOffset(69,176))
type(Key.F4, Key.ALT)

# Quit Teams.
if not exists("tray_icon.png"):
    click("tray_more.png")
rightClick("tray_icon.png")
click(Pattern("tray_menu.png").targetOffset(-41,40))
wait(20)

# Check if the session terminates.
util.check_running()
