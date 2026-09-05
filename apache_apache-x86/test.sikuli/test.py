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
# clean config prints nothing, so the console stays blank. Verify the server started by its
# console window title (Apache icon + C:\Apache24\bin\httpd.exe) rather than a prompt.
wait("httpd-window.png")
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