script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Minimize all windows then open the Turbo cmd prompt
type("d", Key.WIN)
wait(3)
App().focus("C:\\WINDOWS\\system32\\cmd.exe")

# Test of `turbo run` and command line mode.
wait("cmd_window.png")
type("java -jar C:\\tika\\tika-app.jar --help" + Key.ENTER)
wait("cmd_tika_help.png")
type("java -jar C:\\tika\\tika-app.jar -t " + os.path.join(script_path, os.pardir, "resources", "sample.pdf") + Key.ENTER)
wait("cmd_tika_parsed.png")
run("turbo stop test")

# Launch the app.
run("explorer " + util.find_file(util.start_menu, "Tika"))
wait("tika_window.png")

# Basic operations.
click(Pattern("tika_menu_1.png").targetOffset(-21,1))
click(Pattern("tika_menu_file.png").targetOffset(-15,-30))
click(Pattern("file_name.png").targetOffset(36,1))
type(os.path.join(script_path, os.pardir, "resources", "sample.pdf") + Key.ENTER)
wait("tika_parsed.png")

# Check "help".
click("tika_menu_2.png")
click("tika_menu_help.png")
wait("tika_help.png")
type(Key.F4, Key.ALT)
click(Pattern("tika_menu_1.png").targetOffset(-21,1))
click(Pattern("tika_menu_file.png").targetOffset(-23,31))

# Check if the session terminates.
util.check_running()