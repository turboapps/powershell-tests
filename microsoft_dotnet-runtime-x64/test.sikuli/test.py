# The tests for microsoft_dotnet-runtime and microsoft_dotnet-runtime-x64 are almost the same except for the path.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Test.
wait("rt_ready.png")
type(os.path.join(script_path, os.pardir, "resources", "TestConsole.exe-x64", "TestConsole.exe") + Key.ENTER)
wait("console_test.png")
run("turbo stop test")
wait(10)

# Check if the session terminates.
assert("test" not in run("turbo containers"))