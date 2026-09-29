# The tests for python/python, python/python-x64 and python/python-arm64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test(no_min=True)

# Basic operations.
click("cmd_window.png")
type(Key.ENTER)
type("pip install requests" + Key.ENTER)
# pip needs ~25-50 s here on an idle pool and ran past a fixed 60 s under a
# busy one (App Tests 36477444986 / 36500116648, both finishing seconds after
# the FindFailed). While pip runs, cmd titles its window after the command, so
# keep waiting for as long as that title is up; grace=60 is the old budget, the
# 600 s timeout only bounds a pip that is stuck.
util.wait_while_busy("install_success.png", "pip_running.png", timeout=600, grace=60)
type("python" + Key.ENTER)
wait("python_repl.png")
type('1 + 2' + Key.ENTER)
wait("python_math.png")
type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates.
util.check_stopped("test")