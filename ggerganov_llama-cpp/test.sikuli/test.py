script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

# Test turbo run
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
paste('turbo run ggerganov/llama-cpp --using=microsoft/vcredist --offline --name=test -- /C "C:\\llama-cpu\\llama-server.exe" -m %userprofile%\\desktop\\llama-2-7b-chat.Q4_K_M.gguf -n 50 --port 8180 --chat-template llama2')
wait(2)
type(Key.ENTER)

# Test of the app.
wait("ready.png", 120) # It takes time for the model to warm up.
type("d", Key.WIN)
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk")) # launch another command prompt
wait(5)
click("cmd_window.png")
# "cls &" is what makes the wait below mean anything. cmd leaves the line just
# typed at the prompt on screen, and the --data payload in it renders as
# "messages": [{ -- which matches cmd_response.png ("message":{) at 0.815, over
# SikuliX's 0.7 threshold. Without the clear, wait("cmd_response.png", 600)
# matched the echo of the command itself and returned before ENTER had even
# been processed, so the 600 s allowance for CPU inference never applied and
# the test raced ahead with only the 30 s autoWaitTimeout below to cover
# generation. That is how App Tests runs 33949826631 and 33949816065 died at
# success.png while the request was still in flight: their step frames show
# "exit" never echoing, because curl still owned the console. Clearing first
# also starts the response at column 0 of row 0, so "message":{ lands at a
# fixed spot instead of wrapping wherever the echoed command left the cursor.
curl_command = 'cls & curl --request POST --url http://localhost:8180/v1/chat/completions --header "Content-Type: application/json" --data "{\\"messages\\": [{\\"role\\": \\"user\\", \\"content\\": \\"test\\"}]}"'
paste(curl_command)
wait(2)
type(Key.ENTER)
wait("cmd_response.png", 600) # It takes a very long time to get response if no GPU or AVX is used.
wait(5)
type("exit")
wait(2)
type(Key.ENTER)
# The server console is hosted by conhost.exe -- unlike the two Command Prompt
# windows, which Windows Terminal hosts on Win11 24H2 -- and the Win+D above
# minimized it. A single focus() sometimes restores nothing at all: in run
# 33949826631 the screen was still the terminal at this point and a bare
# desktop by the time the wait gave up. Re-assert the focus between polls for
# the timing summary the server prints when it finishes the request.
if not util.focus_and_wait("conhost", "success.png", attempts=12, poll=5):
    wait("success.png")  # still absent: fail with the usual FindFailed
wait(5)
run("turbo stop test")
wait(10)

# Check if the session terminates.
util.check_running()