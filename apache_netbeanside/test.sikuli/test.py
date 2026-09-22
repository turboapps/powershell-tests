script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import time
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("logo.png", 120)
run("turbo stop test")


# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.desktop, "Apache NetBeans IDE"))

# Basic operations.
wait("logo.png", 120)
click("file-menu.png")
click(Pattern("open-file.png").targetOffset(-22,12))
wait("file-open.png")
paste(os.path.join(script_path, os.pardir, "resources", "HelloWorld.java"))
wait(2)
type(Key.ENTER)
# PROBE: film the whole open window instead of waiting once. Saves a frame
# every 3 s for up to 300 s and logs the first second the class line matches,
# so the artifact shows exactly what NetBeans puts on screen between the Open
# dialog closing and the editor painting - which is what a busy witness for
# util.wait_while_busy has to be built from.
_probe_target = Pattern("hello-world-class.png").similar(0.85)
_probe_start = time.time()
_probe_hit = None
_probe_n = 0
while time.time() - _probe_start < 300:
    _probe_el = time.time() - _probe_start
    util._step_capture("probe-%03d-t%03ds" % (_probe_n, int(_probe_el)))
    _probe_n += 1
    if _probe_hit is None and SCREEN.exists(_probe_target, 0) is not None:
        _probe_hit = _probe_el
        Debug.user("PROBE: hello-world-class first matched at t=%.1f s" % _probe_hit)
        # keep filming another 20 s so the settled state is on record too
        _probe_stop = time.time() + 20
        while time.time() < _probe_stop:
            util._step_capture("probe-%03d-t%03ds-after" % (_probe_n, int(time.time() - _probe_start)))
            _probe_n += 1
            wait(3)
        break
    wait(3)
if _probe_hit is None:
    Debug.user("PROBE: hello-world-class never matched within 300 s")
else:
    Debug.user("PROBE: total open time %.1f s" % _probe_hit)
assert _probe_hit is not None, "PROBE: class line never appeared in 300 s"
wait(20)
click("Run-menu.png")
click("run-file.png")
wait("click-me-button.png")
click("click-me-button.png")
type(Key.ENTER)
wait(5)
click("file-menu.png")
click("exit.png")
wait(20)

# Check if the session terminates.
util.check_running()