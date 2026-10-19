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
# The Lightweight API Client can take ~30-40 s to replace the "Unlock Postman"
# page after the click (CI: 1 s on some runs, 28 s on a pass, >30 s on three
# FindFailed runs that show the client fully painted moments later).
wait("get-url.png", 90)
click("get-url.png")
# Paste rather than type: the "Enter a URL or cURL command" tip opens under the
# field while it is being typed into and swallows the rest of the keystrokes
# (App Tests 38526316134 and 38684125927 sent "https://jsonp").
paste("https://jsonplaceholder.typicode.com/todos/1")
# ENTER sends whatever URL the request model holds. On a busy start the pasted
# text can take >1 s to reach the model; an ENTER sent before that sends
# nothing ("Click Send to get a response", empty History) even though the URL
# shows up in the field moments later (App Tests 38988960389, 38988953618).
# The request header above the URL bar switches from "Untitled Request" to the
# URL only once the model has it, so wait for that before pressing ENTER.
wait("request-url.png", 30)
type(Key.ENTER)
wait("json-output.png")
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()