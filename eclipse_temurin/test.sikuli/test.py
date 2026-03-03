# The tests for eclipse/temurin and eclipse/temurin-lts are almost the same except for the shortcut name.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test(no_min=True)

# Minimize the sikulix console
if exists("sikulix-console.png",15):
    click("sikulix-console.png")
    wait(2)
    type(Key.DOWN, Key.WIN)

# Test of `turbo run`.
wait("jre_cmd.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Temurin JDK.lnk"))

# Basic operations.
click("jre_cmd.png")
type(Key.ENTER)
type("java -version")
type(Key.ENTER)
wait("temurin-version.png")
paste('java -jar "' + os.path.join(script_path, os.pardir, "resources", "HelloWorld.jar") + '"')
wait(3)
type(Key.ENTER)
wait("hello_world.png")
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()