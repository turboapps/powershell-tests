# The tests for apache-x64 and apache-x86 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import subprocess
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test(no_min=True)

# Test.
# The image's default startup file is httpd.exe itself (no cmd wrapper), and `httpd -X` with a
# clean config prints nothing, so the console stays blank. Its title is not stable either: XVM
# 26.9.x shows C:\Apache24\bin\httpd.exe, 26.3.18 shows C:\WINDOWS\system32\conhost.exe. Wait
# for the httpd.exe process instead; the "It works!" page below checks that it is serving.
for attempt in range(30):
    if "httpd.exe" in run('tasklist /NH /FI "IMAGENAME eq httpd.exe"'):
        break
    wait(2)
else:
    assert False, "httpd.exe did not start within 60 s"
run('explorer "http://localhost:8080"')
# Maximize the browser so the page text is on screen regardless of the window's saved placement.
wait(5)
type(Key.UP, Key.WIN)
wait("app.png", 30)
wait(5)
util.close_app("Edge")
wait(5)
run("turbo stop test")
wait(10)

# Check if the session terminates.
util.check_stopped("test")