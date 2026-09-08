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
paste('turbo run ggerganov/llama-cpp --using=microsoft/vcredist --offline --name=test' + util.read_extra() + ' -- /C "C:\\llama-cpu\\llama-server.exe" -m %userprofile%\\desktop\\llama-2-7b-chat.Q4_K_M.gguf -n 50 --port 8180 --chat-template llama2')
wait(2)
type(Key.ENTER)

# Test of the app.
wait("ready.png", 120) # It takes time for the model to warm up.
# Win+D is load-bearing: the server console keeps the top of the z-order, so
# without it the command prompt opened below lands underneath and cmd_window.png
# is clipped out of existence (run 34091540254, which never got past the click).
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
# Restore the server console that Win+D minimized and read the timing summary
# it prints when it finishes a request.
#
# Match the session name, not the console host. This used to be
# App("conhost").focus(), which matched the window title Turbo gives the
# session -- "C:\WINDOWS\system32\conhost.exe @test#c5c0ad03" on xvm 26.3.18.
# On 26.9.x the same window is titled "...\cmd.exe @test#fd709707", so
# "conhost" matched nothing, focus() restored nothing, and the test waited out
# its timeout against a bare desktop. That is the whole of the 26.3.18 /
# 26.9.x split in this test's history: 26.3.18.1034 and the 26.3.18 pool VM
# passed (runs 33849047386, 33943398106) while 26.9.20.1047 and 26.9.26.1052
# failed (33849072018, 33949816065, 33949826631). "@test#" comes from
# --name=test above and is in both titles.
if not util.focus_and_wait("@test#", "success.png", attempts=12, poll=5):
    wait("success.png")  # still absent: fail with the usual FindFailed
wait(5)
run("turbo stop test")
wait(10)

# Check if the session terminates.
util.check_running()