# mongodb/communityserver and mongodb/compass use the same test.py script.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("add-connection-button.png")
type("q", Key.CTRL)
type(Key.ENTER)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "MongoDB", "MongoDB Compass.lnk"))

# Activate and maximize the app window.
app_window = App().focus("MongoDB Compass")
if app_window.isValid():
    type(Key.UP, Key.WIN)

# Basic operations.
wait("add-connection-button.png")
click("add-connection-button.png")
wait("connection-name.png")
click("connection-name.png")
type("mongotest" + Key.ENTER)
click("connect-button.png")
wait("server-name.png")
click("server-name.png")
wait("create-db-button.png")
click("create-db-button.png")
wait("db-name.png")
type("testdb" + Key.TAB)
type("testcollection" + Key.TAB)
click("createdb.png")
wait("import-button.png")
click("import-button.png")
wait("file-browser.png")
click("file-browser.png")
type("%localappdata%\\turbo\\containers\\repo\\repos.json")
type(Key.ENTER)
wait("import-confirm.png")
click("import-confirm.png")
wait("db-data.png")
wait(5)

# Quit the app and stop the mongoserver
type("q", Key.CTRL)
type(Key.ENTER)
run("turbo stop mongodbserver")
wait(10)

# Check if the session terminates.
util.check_running()