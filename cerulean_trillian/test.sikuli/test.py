script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username1 = credentials.get("username1")
password1 = credentials.get("password1")
username2 = credentials.get("username2")
password2 = credentials.get("password2")

# Test of `turbo run`.
wait("login-prompt.png",60)
type(Key.F4, Key.ALT)

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Trillian.lnk"))
wait("login-prompt.png",60)
click("username.png")
type(username1)
type(Key.ENTER)
wait("password.png",60)
type(password1)
type(Key.ENTER)
wait("menu.png")

# Launch a second instance of the app and login as a second user
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
type('turbo try trillian --offline --name=trytrillian -d')
type(Key.ENTER)
click("username.png")
type(username2)
type(Key.ENTER)
wait("password.png",60)
type(password2)
type(Key.ENTER)
wait(15)

wait("menu.png")
click("menu.png")
click("send-msg.png")
wait("checkbox.png")
click("checkbox.png")
wait("open.png")
click("open.png")
wait("chat-box.png")
click("chat-box.png")
type("hi" + Key.ENTER)
wait("message-received.png")
click("menu.png")
click("exit.png")
wait(5)
click("menu.png")
click("exit.png")
wait(10)

# Check if the session terminates.
util.check_running()