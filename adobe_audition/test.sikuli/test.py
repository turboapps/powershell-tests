script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)
resources = os.path.join(script_path, os.pardir, "resources")

setAutoWaitTimeout(20)

util.pre_test()

# PROBE (not for merge): reproduce the CEPHtmlEngine crash on the Learn panel's Close Panel that
# 6622e31 stopped triggering, and capture a dump of it. The crash parks the process in a legacy
# "Application Error" box, so WER never writes a dump; the helper dumps CEPHtmlEngine.exe itself
# into the step-frames folder (uploaded with the diagnostics) and the test stops right there.
steps_dir = os.path.join(os.environ['USERPROFILE'], "Desktop", "adobe_audition-steps")
def close_learn_panel_and_check(where):
    if not exists("learn-panel.png", 20):
        Debug.user("PROBE %s: Learn panel not shown, nothing to close" % where)
        return
    click(Pattern("learn-panel.png").targetOffset(8,-28))
    click("close-panel.png")
    Debug.user("PROBE %s: clicked Close Panel" % where)
    wait(8)
    out = run('powershell -NoProfile -ExecutionPolicy Bypass -File "%s" -OutDir "%s"' %
              (os.path.join(resources, "dump-on-app-error.ps1"), steps_dir))
    for line in out.splitlines():
        Debug.user("PROBE %s: %s" % (where, line))
    if "APP_ERROR_FOUND" in out:
        raise FindFailed("PROBE REPRO (%s): CEPHtmlEngine Application Error after Close Panel; dump in adobe_audition-steps" % where)

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test turbo run
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
paste('turbo run audition --using=isolate-edge-wc,creativeclouddesktop --offline --enable=disablefontpreload --name=test' + util.read_extra())
wait(2)
type(Key.ENTER)
if exists("hardware-warning.png",90):
    click(Pattern("hardware-warning.png").targetOffset(-173,7))
    click(Pattern("hardware-warning.png").targetOffset(192,38))
close_learn_panel_and_check("1st launch")
if exists("adobe_login_signout_others.png",10):
    click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
    click(Pattern("adobe_login_continue.png").similar(0.80))
if exists("adobe_login_team.png",10):
    click(Pattern("adobe_login_continue.png").similar(0.80))

wait("audition-title-bar.png",15)
wait(5)
run("turbo stop test")
wait(5)
closeApp("Command Prompt")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Audition"))
if exists("hardware-warning.png",90):
    click(Pattern("hardware-warning.png").targetOffset(-173,7))
    click(Pattern("hardware-warning.png").targetOffset(192,38))
close_learn_panel_and_check("2nd launch")
wait("audition-title-bar.png",15)

# Basic operations.
type("i",Key.CTRL)
wait("import-file.png")
click("import-file.png")
wait(5)
sample = os.path.join(resources,"sample.mp3")
paste(sample)
wait(2)
type(Key.ENTER)
wait("sample-open.png",30)
type("e", Key.CTRL + Key.SHIFT)
wait("export-file.png")
type(Key.ENTER)
if exists("export-warning.png"):
    type(Key.ENTER)
wait(10)
assert(util.file_exists(os.path.join(os.environ['USERPROFILE'], "Documents\\sample_01.mp3"), 5))
type("q",Key.CTRL)
wait(10)
os.system('cmd /c taskkill /f /im "adobe audition.exe" /t')  # adobe bug prevents process from ending

# Check that the session can be ended. A known Adobe bug leaves Audition's
# processes running after it quits, and even after the taskkill above the
# session was still Running 100 s later on every run of App Tests 41147648349,
# 41147655940 and 41147663573. That is the app's behaviour, not Turbo's: give
# it a minute to leave on its own, then stop the session and require that to work.
util.end_session(grace=60)