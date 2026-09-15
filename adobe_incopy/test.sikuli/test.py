script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import subprocess
import time
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(45)
save_path = os.path.join(util.desktop, "test.icml")

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test of `turbo run`.
subprocess.Popen("turbo run incopy --using=creativeclouddesktop,isolate-edge-wc --offline --enable=disablefontpreload --network=test --name=test" + util.read_extra())
wait(3)
type(Key.ENTER)
if exists("adobe_login_signout_others.png",120):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("adobe_login_team.png",10):
    click(Pattern("adobe_login_continue.png").similar(0.80))
wait("incopy_window.png",20)
run("turbo stop test")
closeApp("Command Prompt")

# Let the stopped instance leave the screen before relaunching.
#
# `turbo stop` comes back before the window has gone. In App Tests run 34925411368
# it gave up on the session outright - "Timeout waiting for session %s to stop"
# after 12 s - and still returned 0, and the test walked straight on to the
# shortcut launch. The step frame taken before the wait below and the one taken
# before the wait above the stop are the same screen to within a mean absolute
# difference of 0.002: the stopped instance's window, still painted. The client
# log puts "Application exited: 0" 2.5 s before that frame, so what was on the
# screen was the dead instance's window rather than a running application. So
# `wait("incopy_window.png",120)` matched that window and returned at once,
# spending none of its 120 s on the instance the shortcut had just launched. Ten
# seconds later the old window was gone and the new InCopy was on its splash
# ("Initializing plug-ins..."), so the only budget left for it was the 45 s
# autoWaitTimeout on the click below - short of the >63 s that launch was still
# taking when the test gave up.
#
# waitVanish states the precondition in the same terms the following wait depends
# on - pixels - so a stop that really does leave the application running fails
# here, at the cause, instead of at an image several steps later.
assert waitVanish("incopy_window.png", 120), "the stopped InCopy window is still on screen"

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe InCopy"))

# Basic operations.
# 180 s rather than 120 s: the relaunch in run 34925411368 was still initializing
# plug-ins 63 s in and was never measured to completion, so the old budget has no
# measured margin now that it is being spent on the right instance. The Debug line
# records what the launch actually costs on the pool VMs.
launch_start = time.time()
wait("incopy_window.png",180)
Debug.user("InCopy window up %d s after the shortcut launch" % (time.time() - launch_start))
wait(10)
click("incopy_window.png")
type("n", Key.CTRL)
wait("new_document.png")
type(Key.ENTER)
wait("new_file.png")
paste("test")
click(Pattern("new_file.png").targetOffset(61,12))
wait("layout_view.png")
type("s", Key.CTRL + Key.SHIFT)
wait("save_location.png")
paste(save_path)
type(Key.ENTER)
wait("user.png")
paste(save_path) 
type(Key.ENTER)
assert(util.file_exists(save_path, 5))
type("q", Key.CTRL)
wait(30)
run("explorer " + save_path)
wait("untitled-1.png",120)

# Check "help".
# Launch help twice as it sometimes fails the first time
type(Key.F1)
wait(10)
util.close_app("Edge")
type(Key.F1)
wait("help_url.png",30)
util.close_app("Edge")
wait(10)
type("q", Key.CTRL)
wait(10)

# Check if the session terminates.
util.check_running()