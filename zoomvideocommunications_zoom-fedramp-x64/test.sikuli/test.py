# The tests for zoomvideocommunications/zoom and zoomvideocommunications/zoom-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("zoom_window.png")
run("turbo stop test")
wait(10)

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Zoom", "Zoom Workplace.lnk"))
wait("zoom_window.png")
if exists("dont-show-vdi.png",10):
    click("dont-show-vdi.png")
click("sign-in.png")
wait("down-arrow.png")
wait(5)
click("down-arrow.png")
wait("zoomgov-com.png")
click("zoomgov-com.png")
type(Key.F4, Key.ALT)
wait(10)
if exists("systray-arrow.png"):
    click("systray-arrow.png")
    wait(5)
    if exists("zoom-systray.png"):
        hover("zoom-systray.png")
        
# URL handler.
run('explorer "https://zoom.us/test"')
wait("join-test-button.png")
click("join-test-button.png")
# The Edge external-protocol dialog ("Open Zoom Workplace?") can take longer
# than the default wait to appear, and the Join click is occasionally swallowed
# while the page is still settling. Give it a longer window, then click again.
if not exists("url-handler-checkbox.png",60):
    click("join-test-button.png")
wait("url-handler-checkbox.png",60)
click("url-handler-checkbox.png")
type(Key.TAB)
wait(2)
type(Key.TAB)
wait(2)
type(Key.ENTER)
wait("join-mtg.png")
click("join-mtg.png")
wait("yes-sound.png")
click("yes-sound.png")
wait("yes-sound.png")
click("yes-sound.png")
wait("end-test.png")
click("end-test.png")
util.close_app("Edge")
# PROBE ONLY: stand a notification banner in the tray corner, the way run
# 35063712843 had one there. The control branch (zoom-probe-toast-control)
# runs this same raiser against main's exit dance and fails on it.
run('powershell -ExecutionPolicy Bypass -File "' + os.path.join(script_path, "probe-toast.ps1") + '"')
wait(5)
# The Zoom tray icon is pinned well above the 0.74 that a Windows Security
# notification banner's blue shield scores against it: a banner shares the
# bottom-right corner with the tray flyout, and at SikuliX's 0.7 default the
# right-click went to the toast instead (App Tests run 35063712843).
zoom_systray = Pattern("zoom-systray.png").similar(0.9)
if exists("systray-arrow.png"):
    rightClick(util.show_tray_icon(zoom_systray))
    # A banner arriving between the flyout opening and the right-click covers
    # the icon and swallows the menu; reopen a clear flyout and click again.
    if not exists("exit-zoom.png", 10):
        rightClick(util.show_tray_icon(zoom_systray))
    click("exit-zoom.png")
wait(20)

# Check if the session terminates.
util.check_running()

# PROBE ONLY: the threshold half, against SikuliX's own matcher rather than an
# offline stand-in. probe-run-35063712843-frame.jpg is the step frame captured
# immediately before the right-click that failed - the tray flyout open, the
# Windows Security banner over it, the Zoom icon nowhere. At the 0.7 default
# zoom-systray.png finds the banner's blue shield in it; at the 0.9 this PR
# pins it to, it finds nothing.
loose = Finder(os.path.join(script_path, "probe-run-35063712843-frame.jpg"))
loose.find(Pattern("zoom-systray.png").similar(0.7))
assert loose.hasNext(), "probe: 0.7 found nothing in the failing frame - the frame or the reference changed"
hit = loose.next()
Debug.user("probe: 0.7 matches the failing frame at (%d,%d) score %.3f"
           % (hit.getX() + hit.getW() / 2, hit.getY() + hit.getH() / 2, hit.getScore()))
assert 1500 < hit.getX() + hit.getW() / 2 < 1650, "probe: 0.7 did not land on the banner"

tight = Finder(os.path.join(script_path, "probe-run-35063712843-frame.jpg"))
tight.find(Pattern("zoom-systray.png").similar(0.9))
assert not tight.hasNext(), "probe: 0.9 still matches the banner - the threshold is not enough"
Debug.user("probe: 0.9 rejects the failing frame")
