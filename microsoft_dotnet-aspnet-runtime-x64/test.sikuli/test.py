# The tests for microsoft_dotnet-aspnet-runtime, microsoft_dotnet-aspnet-runtime-x64, microsoft_dotnet-desktop-runtime and microsoft_dotnet-desktop-runtime-x64 are the same.

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

# Test.
wait("dn_asp_rt_ready.png")
run('explorer "http://localhost:5000"')
wait("app.png")
wait(5)
closeApp("Edge")
wait(5)
run("turbo stop test")
wait(10)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))