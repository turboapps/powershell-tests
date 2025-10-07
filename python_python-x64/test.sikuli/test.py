# The tests for python/python and python/python-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test(no_min=True)

# Minimize the sikulix console
if exists("sikulix-console.png"):
    App().focus("java.exe")
    type(Key.DOWN, Key.WIN)

# Basic operations.
click("cmd_window.png")
type(Key.ENTER)
type("pip install requests" + Key.ENTER)
wait("install_success.png", 60)
type("python" + Key.ENTER)
wait("python_repl.png")
type('1 + 2' + Key.ENTER)
wait("python_math.png")
type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))