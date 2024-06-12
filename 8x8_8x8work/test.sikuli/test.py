script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Test of `turbo run`.
wait("8x8-login.png")
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.desktop, "8x8 Work"))

# Basic operations.
wait("8x8-login.png")

type(Key.F4, Key.ALT)
os.system('cmd /c taskkill /f /im "8x8 work.exe" /t')
wait(10)

# Check if the session terminates.
util.check_running()