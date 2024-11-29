# The tests for webex/webex and webex/webex-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(60)
util.pre_test()

# Test of `turbo run`.
wait("webex_eula.png")
click(Pattern("webex_eula.png").targetOffset(-94,242))
wait("webex_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Webex", "Webex.lnk"))
click(Pattern("webex_eula.png").targetOffset(-94,242))
wait("webex_window.png")
type(Key.F4, Key.ALT)

# URL handler.
run('explorer "https://meet361.webex.com/meet/pr26330258604"')
click(Pattern("url_handler.png").targetOffset(129,50))
closeApp("Edge")
wait("webex_window.png")
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()