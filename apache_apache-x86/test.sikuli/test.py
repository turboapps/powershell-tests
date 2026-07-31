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
wait("httpd-running.png")
run('explorer "http://localhost:8080"')
wait("app.png")
wait(5)
closeApp("Edge")
wait(5)
run("turbo stop test")
wait(10)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))