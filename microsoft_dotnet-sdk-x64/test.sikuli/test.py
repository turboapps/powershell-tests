# The tests for microsoft_dotnet-sdk and microsoft_dotnet-sdk-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

# Minimize the sikulix console
if exists("sikulix-console.png"):
    App().focus("java.exe")
    type(Key.DOWN, Key.WIN)

# Test.
wait("sdk_ready.png")
paste('dotnet new console -n TestConsole -o "%USERPROFILE%\Desktop\dotnet\project"')
type(Key.ENTER)
wait("restore_succeeded.png")
run("turbo stop test")
wait(10)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))