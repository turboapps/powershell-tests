# The tests for microsoft_dotnet-runtime, microsoft_dotnet-runtime-x64 and microsoft_dotnet-runtime-arm64 are almost the same except for the path.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test(no_min=True)

# Test.
# The container console does not necessarily own the keyboard when the test
# starts - see util.focus_console - so take it before pasting. Without this the
# paste and ENTER can land on the taskbar (Start button focused) and open the
# Start menu while the console sits at an empty prompt (App Tests run 38988960389
# / 38988963564, arm64).
util.focus_console("rt_ready.png")
paste(os.path.join(script_path, os.pardir, "resources", "TestConsole.exe-arm64", "HelloWorld.exe"))
wait(3)
type(Key.ENTER)
wait("console_test.png")
run("turbo stop test")
wait(10)

# Check if the session terminates.
util.check_stopped("test")