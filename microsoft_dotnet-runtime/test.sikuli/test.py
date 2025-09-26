# The tests for microsoft_dotnet-runtime and microsoft_dotnet-runtime-x64 are almost the same except for the path.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test(no_min=True)

# Minimize all windows then open the Turbo cmd prompt
type("d", Key.WIN)
wait(3)
App().focus("C:\\WINDOWS\\system32\\cmd.exe")

# Test.
wait("rt_ready.png")
paste(os.path.join(script_path, os.pardir, "resources", "TestConsole.exe-x86", "TestConsole.exe"))
type(Key.ENTER)
wait("console_test.png")
run("turbo stop test")
wait(10)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))