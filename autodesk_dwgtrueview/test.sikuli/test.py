script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

dwgfile_path = os.path.join(script_path, os.pardir, "resources", "blocks_and_tables_-_metric.dwg")

setAutoWaitTimeout(60)
util.pre_test()

app_window = "Autodesk DWG TrueView"

# Autodesk shows a modal "Privacy Settings" dialog on a first launch. It covers
# the Start tab and dims the window behind it, so app-loaded.png is only ever a
# washed-out near-match while it is up: App Tests run 33898089779 failed with
# "FindFailed ( app-loaded.png: (109x51) seen at (32, 123) with 0.92 )" and a
# screenshot showing the dialog. Which launch it lands on depends on how much of
# the profile the merge-user sandbox carried over, so dismiss it wherever it
# appears rather than at one fixed point in the script.
def dismiss_privacy_dialog():
    if exists("privacy-dialog.png", 1):
        click("privacy-ok.png")
        wait(2)
        return True
    return False

# Wait for the Start tab, clearing the privacy dialog if that is what is on
# screen. Ends in a plain wait() so a genuine failure still reports
# app-loaded.png the way it always did.
def wait_app_loaded(timeout=120):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if dismiss_privacy_dialog():
            continue
        if exists("app-loaded.png", 2):
            break
    wait("app-loaded.png", 10)
    # Focus the main window rather than clicking app-loaded.png: that image is
    # the wordmark inside the Start tab's embedded browser pane, and clicking it
    # leaves focus in the pane, where the app's accelerators are swallowed (see
    # the Ctrl+O retry below).
    util.activate_app_window(app_window, 10)
    wait(10)

# Test of `turbo run`.
wait_app_loaded()
type(Key.F4, Key.ALT) # Close app.
# Let DWG TrueView finish its own exit before the session is stopped.
#
# This is the only close in the test that a `turbo stop` follows, and it is the
# only one that has ever produced a crash dump. `turbo stop` does not kill the
# process: the VM posts WM_CLOSE to every top-level window in the container
# (CSystemManager::TerminateSelfGracefullyCallback), so a stop issued while the
# Alt+F4 teardown is still running delivers a SECOND close into a shutdown that
# is already in progress. DWG TrueView does not guard against that: about a
# second later, unloadAllModules tears the managed ObjectARX layer down twice
# and an MFC CString buffer is freed twice, and dwgviewr.exe dies with c0000374
# STATUS_HEAP_CORRUPTION (bucket
# HEAP_CORRUPTION_ACTIONABLE_BlockNotBusy_DOUBLE_FREE, ucrtbase!free_base <-
# mfc140u!CStringT::~CStringT). SikuliX never notices - the app is closing
# anyway, every step frame is clean and the script runs to the end - and the job
# is failed by the crash-dump gate instead.
#
# Measured at 8/22 cycles with the stop racing the teardown and 0/27 with the
# stop issued after the process had gone (probe branch
# probe-dwgtrueview-turbostop-race, five App Tests runs, Fisher one-sided
# p = 0.0007). Most recently on xvm 26.9.48 in App Tests run 35654098667
# (dwgviewr.exe.8160.dmp).
#
# The application exits ~2 s after Alt+F4, so this normally costs nothing. Wait
# on the process and not on the session: Autodesk leaves AdskAccessService /
# ADPClientService inside the container, which keeps the session Running well
# past the application's own exit.
# SABOTAGE PROBE - DO NOT MERGE. The wait this branch exists to test is
# neutered: it is pointed at a process name that is never running, so it returns
# at once and the `turbo stop` goes out into the teardown exactly as it does on
# main. Everything else on this branch, including util.wait_process_gone itself,
# is byte-identical to dwgtrueview-stop-after-exit, so a crash here and none on
# that branch can only be the wait.
util.wait_process_gone("dwgviewr-sabotage-never-running.exe", 0)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "DWG TrueView"))
wait_app_loaded()
type("o", Key.CTRL)
# Ctrl+O is dropped when focus has not settled on the main window, and the Open
# dialog never appears: this step failed in 2 of 10 runs (App Tests runs
# 33898073231 and 33898092961), both times with the Start tab fully rendered and
# no dialog on screen. Re-focus and press it again before giving up.
if not exists("file-open.png", 15):
    type(Key.ESC)
    wait(1)
    util.activate_app_window(app_window, 10)
    type("o", Key.CTRL)
wait("file-open.png")
click("file-open.png")
type(dwgfile_path)
type(Key.ENTER)
wait("dwg-tab.png")
wait(5)
type(Key.F1)
wait("help.png",120)
wait(5)
type(Key.F4, Key.ALT) # Close help.
wait(5)
type(Key.F4, Key.ALT) # Close app.
wait(5)
os.system('cmd /c taskkill /f /im "AcHelp2.exe" /t')
os.system('cmd /c taskkill /f /im "ADPClientService.exe" /t')

# Test file association.
run("explorer " + dwgfile_path)
wait("dwg-tab.png")
click("dwg-tab.png")
type(Key.F4, Key.ALT) # Close app.
wait(10)
os.system('cmd /c taskkill /f /im "ADPClientService.exe" /t')
os.system('cmd /c taskkill /f /im "AdskAccessService.exe" /t')
wait(20)

# Check if the session terminates.
util.check_running()