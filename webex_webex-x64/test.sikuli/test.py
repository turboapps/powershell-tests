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
wait("webex_eula.png",120)
click(Pattern("webex_eula.png").targetOffset(-94,242))
wait("welcome.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Webex", "Webex.lnk"))
wait("webex_eula.png",120)
click(Pattern("webex_eula.png").targetOffset(-94,242))
wait("welcome.png")
type(Key.F4, Key.ALT)

# URL handler.
run('explorer "https://meet361.webex.com/meet/pr26330258604"')
wait("url_handler.png")
click("url_handler.png")
type(Key.TAB)
wait(2)
type(Key.TAB)
wait(2)
type(Key.ENTER)
util.close_app("Edge")
if exists("new-webex.png",10):
    click("new-webex.png")
    click("always.png")
# The meeting window takes 10-30 s to paint, and the "Can't use computer for
# audio" modal (CI has no audio devices) arrives with it. Wait for the window
# first, then dismiss the modal: if the modal is still up, the Alt+F4 below
# closes it instead of the meeting window and the login window never returns.
wait("room.png",60)
if exists(Pattern("mic-ok.png").similar(0.90),10):
    util.click_until_gone(Pattern("mic-ok.png").similar(0.90))
click("room.png")
wait(3)
# A modal that arrived after the check above eats the Alt+F4; the meeting
# window then stays up. Dismiss it and close the window again.
for attempt in range(3):
    type(Key.F4, Key.ALT)
    if exists("welcome.png",20):
        break
    Debug.user("meeting window still open after Alt+F4 (attempt %d)" % (attempt + 1))
    if exists(Pattern("mic-ok.png").similar(0.90),0):
        util.click_until_gone(Pattern("mic-ok.png").similar(0.90))
    click("room.png")
    wait(3)
wait("welcome.png",1)
type(Key.F4, Key.ALT)
os.system('cmd /c taskkill /f /im "webexhost.exe" /t')
wait(20)

# Check if the session terminates.
util.check_running()