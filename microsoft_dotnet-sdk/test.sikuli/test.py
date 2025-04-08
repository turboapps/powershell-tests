# The tests for microsoft_dotnet-sdk and microsoft_dotnet-sdk-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

# Test.
wait("sdk_ready.png")
type('dotnet new console -n TestConsole -o "%USERPROFILE%\Desktop\dotnet\project"' + Key.ENTER)
wait("restore_succeeded.png")
run("turbo stop test")
wait(10)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))