script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import re
import util
reload(util)
addImagePath(include_path)
resources = os.path.join(script_path, os.pardir, "resources")

setAutoWaitTimeout(20)

# VALIDATION ONLY (not for merge): the chronic CEPHtmlEngine D3AD crash after
# "Close Panel" leaves a hard-error box that eats every later keystroke, so the
# teardown under test is never reached. Dismiss it so the run gets that far.
def dismiss_cep_error():
    wait(5)
    for attempt in range(3):
        if not App().focus("Application Error").isValid():
            return
        Debug.user("VALIDATION: dismissing CEPHtmlEngine Application Error box (attempt %d)" % (attempt + 1))
        type(Key.ENTER)
        wait(3)

util.pre_test()

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
if exists("learn-panel.png",20):
    click(Pattern("learn-panel.png").targetOffset(8,-28))
    click("close-panel.png")
    dismiss_cep_error()
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
if exists("learn-panel.png",20):
    click(Pattern("learn-panel.png").targetOffset(8,-28))
    click("close-panel.png")
    dismiss_cep_error()
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

# Ctrl+Q takes Audition's window down, but on some runs the process stays
# behind with no window and keeps the session Running (App Tests 38432578750:
# bare desktop, session still Running 95 s after Ctrl+Q). The taskkill added
# for that named "audition.exe", which matches no process - the executable is
# "Adobe Audition.exe" - so it never fired. Give the app the time a clean quit
# takes, then stop it by its real name, and log which Adobe processes are
# still alive so a session that outlives that is attributable from the log.
def log_adobe_processes(label):
    rows = []
    for line in run("tasklist /FO CSV /NH").splitlines():
        fields = re.findall(r'"([^"]*)"', line)
        if len(fields) >= 2 and re.search(r"(?i)adobe|audition|cep|ccx|coresync|node\.exe|creative|dynamiclink", fields[0]):
            rows.append("%s(%s)" % (fields[0], fields[1]))
    Debug.user("audition %s: %s" % (label, ", ".join(rows) or "no Adobe processes"))

if util.wait_process_gone("Adobe Audition.exe", 60) < 0:
    util.stop_processes("Adobe Audition.exe")
log_adobe_processes("after quit")

# Check if the session terminates.
wait(10)
util.check_running()