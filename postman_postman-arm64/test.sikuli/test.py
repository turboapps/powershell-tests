script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
if exists("light-client.png",20):
    click("light-client.png")
if exists("continue-without-account.png",20):
    click("continue-without-account.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Postman", "Postman.lnk"))

# Basic operations.
if exists("light-client.png",20):
    click("light-client.png")
if exists("continue-without-account.png",20):
    click("continue-without-account.png")
wait("open-api-client.png")
click("open-api-client.png")
wait("get-url.png")
click("get-url.png")
type("https://jsonplaceholder.typicode.com/todos/1")
type(Key.ENTER)
wait("json-output.png")
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()