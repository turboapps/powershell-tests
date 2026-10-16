script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

import time

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

# The server console is not always the same window. On xvm 26.x it is a classic
# conhost window titled "...\conhost.exe @test#<id>" (or "...\cmd.exe @test#<id>"),
# but on xvm 25.10.4 Windows Terminal hosts it, titled "C:\WINDOWS\system32\cmd.exe"
# and drawn in WT's font (~1.13x wider glyphs), where no conhost crop can match
# (run 38832388742: the server was listening at 34 s, ready.png scored 0.28).
# So every image read off the server console has one crop per host, and the
# window is focused by either title. "system32" is in both server titles but not
# in the harness prompts ("Administrator: Command Prompt"); "cmd.exe" would be
# read as a process name and could focus a harness cmd.exe instead.
# Both crops are also NEW text: the old ready.png/success.png were cut from an
# older llama.cpp ("main: server is listening on ...", a stacked timing block).
# The current build (image 10537) logs "llama_server: listening on ..." and
# prefixes the timings with "print_timing: id N | task N |", and the old
# ready.png passed on conhost only as a 0.717 near miss on different words.
READY = ["ready.png", "ready_wt.png"]
# conhost restores the server console after Win+D at either of two font sizes
# (14.4 px line pitch in run 38808757196, 16 px in run 38857253431), hence two
# conhost crops of the timing line.
SUCCESS = ["success.png", "success_conhost.png", "success_wt.png"]
SERVER_WINDOWS = ["@test#", "system32"]

# Poll for any of images; on timeout fail with a FindFailed on the first one.
# SCREEN.exists bypasses util's step-frame hooks, so the poll does not flood the
# step screenshots; the final wait() still records the FAILED frame.
def wait_any(images, timeout, windows=None, poll=5):
    deadline = time.time() + timeout
    while True:
        if windows:
            for window in windows:
                App(window).focus()
            wait(1)
        for image in images:
            if SCREEN.exists(image, 0):
                Debug.user("wait_any: matched %s" % image)
                return image
        if time.time() >= deadline:
            break
        wait(poll)
    return wait(images[0], 0)

# Test turbo run
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
paste('turbo run ggerganov/llama-cpp --using=microsoft/vcredist --offline --name=test' + util.read_extra() + ' -- /C "C:\\llama-cpu\\llama-server.exe" -m %userprofile%\\desktop\\llama-2-7b-chat.Q4_K_M.gguf -n 50 --port 8180 --chat-template llama2')
wait(2)
type(Key.ENTER)

# Test of the app.
wait_any(READY, 120) # It takes time for the model to warm up.
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
# --name=test above and is in both titles. A WT-hosted console has neither, so
# SERVER_WINDOWS adds "system32" (see the top of the file).
wait_any(SUCCESS, 90, windows=SERVER_WINDOWS)
wait(5)
run("turbo stop test")
wait(10)

# Check if the session terminates.
util.check_running()