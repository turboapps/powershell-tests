# The tests for python/python and python/python-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import time
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test(no_min=True)

# Basic operations.
click("cmd_window.png")
type(Key.ENTER)
type("pip install requests" + Key.ENTER)
# PROBE: measure how long pip install takes; frame every 30 s.
_t0 = time.time()
_last = 0
while SCREEN.exists("install_success.png", 0) is None:
    _el = time.time() - _t0
    if _el - _last >= 30:
        _last = _el
        Debug.user("PROBE pip still running at %d s" % _el)
        util._step_capture("probe-pip-%03d" % int(_el))
    if _el > 600:
        break
    wait(1)
Debug.user("PROBE pip install finished after %d s" % (time.time() - _t0))
wait("install_success.png", 5)
type("python" + Key.ENTER)
wait("python_repl.png")
type('1 + 2' + Key.ENTER)
wait("python_math.png")
type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates.
util.check_stopped("test")