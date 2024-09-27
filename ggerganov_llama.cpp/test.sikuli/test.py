script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of the app.
wait("ready.png", 120) # It takes time for the model to warm up.
type(Key.DOWN, Key.WIN) # Hide the llama cli window.

click("cmd_window.png")
curl_command = 'curl --request POST --url http://localhost:8180/v1/chat/completions --header "Content-Type: application/json" --data "{\\"messages\\": [{\\"role\\": \\"user\\", \\"content\\": \\"test\\"}]}"'
type(curl_command + Key.ENTER)
wait("cmd_response.png", 600) # It takes a very long time to get response if no GPU or AVX is used.
type("exit" + Key.ENTER)

App().focus("cmd.exe")
App().focus("cmd.exe") # Make the llama cli window visable.
wait("success.png")
run("turbo stop test")
wait(10)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))