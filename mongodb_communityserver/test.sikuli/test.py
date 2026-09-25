# mongodb/communityserver and mongodb/compass use the same test.py script.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import subprocess
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

shortcut = os.path.join(util.start_menu, "MongoDB", "MongoDB Compass.lnk")

# Wait for Compass to finish starting, and relaunch it once if it never does.
#
# add-connection-button.png is the full-width "Add new connection" button in the
# sidebar, not the smaller one on the Welcome tab. The sidebar shows it only once
# Compass has loaded the saved connections (an empty list, on a fresh sandbox),
# and until then it draws three grey placeholder rows under "CONNECTIONS (...)".
# So this image says the app is usable, not just that the window is up.
#
# Now and then Compass stalls on the way there, before the image appears and
# before the old 30 s wait ran out:
# - App Tests run 35935367711 (xvm 26.9.48): no Compass window at all, 56 s
#   after the container reported "Application launched". The mongod console was
#   up and there was no crash dump.
# - Diagnostic run 36042232394: the window came up, but the sidebar was still on
#   its placeholders 61 s after MongoDBCompass.exe started. The VM log shows
#   why nothing was going to change. In a passing launch the main process opens
#   Roaming\MongoDB Compass\Connections 10 s in, as soon as the renderer asks
#   for it. In this one the renderer never asked: from +4 s to the end its only
#   activity is the 60 fps redraw of the placeholder shimmer, and main never
#   touched Connections or AtlasState. No syscall failed and nothing crashed.
#   Compass's startup was waiting on itself, so a longer wait would not help.
#
# Six runs dispatched the same day passed, 3 on the pool VM and 3 on 26.9.48,
# and in each the sidebar had already loaded when the first step frame was
# taken. A fresh launch is what gets past it. `relaunch` stops the stuck
# instance and starts a new one the same way the test did the first time.
# FindFailed if the second launch also stalls, so a real failure still reads as
# FindFailed on this image.
def compass_ready(relaunch, attempts=2, timeout=60):
    for attempt in range(attempts):
        if attempt:
            relaunch()
        if util.focus_and_wait("MongoDB Compass", "add-connection-button.png", attempts=timeout // 10, poll=10):
            if attempt:
                Debug.user("compass_ready: Compass was ready after %d launches" % (attempt + 1))
            # Maximize. The rest of the test finds each image again, so moving
            # the window after the match does not matter.
            type(Key.UP, Key.WIN)
            return
        Debug.user("compass_ready: launch %d of %d: no sidebar Add new connection after %d s"
                   % (attempt + 1, attempts, timeout))
    wait("add-connection-button.png", 0)

# Stop every running Compass session, and only those. The listing's Images
# column tells them apart from mongodbserver (mongodb/communityserver) and from
# the sikulixide session running this script, which must never be stopped. The
# `turbo try` session and the installed shortcut's session are both Compass.
def stop_compass():
    for line in run("turbo sessions -l").splitlines():
        fields = line.split()
        if len(fields) > 2 and fields[2].startswith("mongodb/compass") and "Running" in fields:
            run("turbo stop " + fields[0])
    util.wait_process_gone("MongoDBCompass.exe", max_wait=60)

# The first launch is Test.ps1's TryTurboApp; start the replacement the same
# way, flags included (util.try_verb gives `run` on a diagnostic run).
def relaunch_try():
    stop_compass()
    subprocess.Popen("turbo " + util.try_verb() + " mongodb/compass --name=test"
                     " --enable=disablefontpreload,usedllinjection,cachefileinfo --network=test"
                     " --disable-proxy-resolve-via-proxy -d" + util.read_extra())

# The second launch is the installed shortcut.
def relaunch_shortcut():
    stop_compass()
    run("explorer " + shortcut)

# Test of `turbo run`.
compass_ready(relaunch_try)
type("q", Key.CTRL)
wait(3)
type(Key.ENTER)
run("turbo stop test")

# Launch the app.
run("explorer " + shortcut)

# Basic operations.
compass_ready(relaunch_shortcut)
click("add-connection-button.png")
wait("connection-name.png")
click("connection-name.png")
paste("mongotest")
type(Key.ENTER)
wait("server-name.png")
click("server-name.png")
wait("create-db-button.png")
click("create-db-button.png")
wait("db-name.png")
paste("testdb")
type(Key.TAB)
paste("testcollection")
type(Key.TAB)
click("createdb.png")
wait("import-button.png")
click("import-button.png")
wait("file-browser.png")
click("file-browser.png")
paste("%localappdata%\\turbo\\containers\\repo\\repos.json")
type(Key.ENTER)
wait("import-confirm.png")
click("import-confirm.png")
wait("db-data.png")
wait(5)

# Quit the app and stop the mongoserver
type("q", Key.CTRL)
wait(3)
type(Key.ENTER)
run("turbo stop mongodbserver")
wait(20)

# Check if the session terminates.
util.check_running()