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
wait("fedramp-login.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Webex", "Webex.lnk"))
click(Pattern("webex_eula.png").targetOffset(-94,242))
wait("fedramp-login.png")
type(Key.F4, Key.ALT)

# URL handler.
run('explorer "https://meet361.webex.com/meet/pr26330258604"')
click(Pattern("url_handler.png").targetOffset(129,50))
closeApp("Edge")
if exists(Pattern("mic-ok.png").similar(0.90),20):
    click(Pattern("mic-ok.png").similar(0.90))
wait("join-meet.png",20)
click("join-meet.png")
wait(3)
type(Key.F4, Key.ALT)
wait("fedramp-login.png",20)
type(Key.F4, Key.ALT)
os.system('cmd /c taskkill /f /im "webexhost.exe" /t')
wait(20)

# Check if the session terminates.
util.check_running()