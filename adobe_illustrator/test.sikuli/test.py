script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import subprocess
import time
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)

util.pre_test()

save_location = os.path.join(util.desktop, "Untitled-1.ai")

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Wait for the Illustrator Home page, dismissing the optional What's New and
# "sign out of other devices" dialogs if either turns up meanwhile, all inside
# ONE budget. The old chain (exists(whats_new,100) + exists(signout,20) +
# wait(ai_window,20)) gave the first launch 140 s and burned 100 s of it on a
# What's New dialog Illustrator 30.x no longer shows. Cold first launch on the
# 4-CPU CI VM takes 100-150 s: run 38498033095 (10-14) Home by ~103 s, run
# 38808757196 (10-15) still an empty skeleton at 123 s and painted at ~150 s,
# 10 s past the old deadline. SCREEN.exists is used for the polls so they do
# not flood the step-frame cap; the final wait() captures the FAILED frame.
def wait_for_home(timeout):
    end = time.time() + timeout
    while time.time() < end:
        if SCREEN.exists("ai_window.png", 0):
            return
        if SCREEN.exists("whats_new.png", 0):
            type(Key.ESC)
        elif SCREEN.exists("adobe_login_signout_others.png", 0):
            click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
            click(Pattern("adobe_login_continue.png").similar(0.80))
        wait(5)
    wait("ai_window.png", 1)

# Test of `turbo run`.
subprocess.Popen("turbo run illustrator --using=creativeclouddesktop,isolate-edge-wc --offline --enable=disablefontpreload --network=test --name=test" + util.read_extra())
wait_for_home(60)
run("turbo stop test")
wait(10)

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Illustrator"))
wait_for_home(240)

# Basic operations.
wait(10)
click(Pattern("ai_window.png").targetOffset(-2,-7))
wait(10)
click(Pattern("open_location.png").targetOffset(24,0))
wait(3)
paste("C:\\Program Files\\Adobe\\Adobe Illustrator 2026\\Cool Extras\\en_US\\Templates\\Blank Templates\\Tshirt.ait")
type(Key.ENTER)
wait("tshirt.png")
click("tshirt.png")
wait(10)
type("s", Key.CTRL)
wait("save_location.png")
wait(3)
paste(save_location)
type(Key.ENTER)
click(Pattern("save_options.png").targetOffset(-49,-1))
assert(util.file_exists(save_location, 5))
type("w", Key.CTRL)
wait(10)
run("explorer " + save_location)
wait("tshirt.png")
type(Key.F1)
wait("help.png")
type(Key.ESC)
wait(3)
type("q",Key.CTRL)
wait(10)

# Check if the session terminates.
util.check_running()
