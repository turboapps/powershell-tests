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
# The container console does not necessarily own the keyboard when the test
# starts - see util.focus_console - so take it before pasting. Without this the
# paste and ENTER can land on the taskbar (Start button focused) and open the
# Start menu while the console sits at an empty prompt (App Tests run 38988960389
# / 38988963564, arm64).
util.focus_console("sdk_ready.png")
paste('dotnet new console -n TestConsole -o "%USERPROFILE%\Desktop\dotnet\project"')
wait(3)
type(Key.ENTER)
wait("restore_succeeded.png")
run("turbo stop test")
wait(10)

# Check if the session terminates.
util.check_stopped("test")