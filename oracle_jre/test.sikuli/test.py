# The tests for oracle/jre and oracle/jre-x64 are the same.

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
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Java Runtime"))

# Basic operations.
click("jre_cmd.png")
type(Key.ENTER)
type("java -version" + Key.ENTER)
wait("java_version.png")
type('java -jar "' + os.path.join(script_path, os.pardir, "resources", "HelloWorld.jar") + '"' + Key.ENTER)
wait("hello_world.png")
type(Key.F4, Key.ALT)
wait(10)

# Check if the session terminates.
util.check_running()