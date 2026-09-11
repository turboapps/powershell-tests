# The tests for google/chrome and google/chrome-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import time
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# The TreeSize main window, whether or not the first-run splash is over it: the
# "Select scan target" ribbon button sits above the splash, and it is the only
# reference here that is unique to the app. program-files.png cannot stand in
# for it - that one is TreeSize's address bar, and it scores 0.69 against
# Explorer's own "Program Files" row, too close to SikuliX's 0.7 threshold to
# tell the two windows apart.
TREESIZE_WINDOW = "select-scan-target.png"

# Enough of the main window's title - "C:\Program Files\ - TreeSize
# (Administrator)  (TRIAL VERSION)" - to activate it without matching the
# trial splash, whose own title bar reads just "TreeSize".
TREESIZE_TITLE = "TreeSize (Administrator)"

# Click TreeSize's "Easily Getting Started!" trial splash away if it is up, and
# say whether it was.
#
# The splash is modal over the main window and does not answer Alt+F4 itself, so
# every wait and every close has to be able to clear it. It also comes up more
# than once: in App Tests runs 34269861733 and 34269865181 a second splash
# arrived moments after the first had been dismissed, with the scan already
# under way.
#
# Each click dismisses the splash that is up, but a replacement follows, so a
# run needs two or three clicks before the sequence ends - in App Tests run
# 34423192441 the link was clicked three times and a splash was up again after
# each of the first two. The LAST instance is the one that can go without being
# clicked: in run 34423171312 it left about six seconds after appearing, with no
# click delivered. (The first instance does not do this - probe run 34542455584
# sat on one for 60 s and it never moved - so the splash cannot be waited out.)
#
# So the look and the click have to be one step. Click
# the match exists() already returned rather than click("continue-with-trial.png"),
# which runs a SECOND full-screen search - one that inherits the ambient
# setAutoWaitTimeout(30) - and raises FindFailed when the splash left in the gap
# between the two, which is the outcome this function wants. Run 34423171312 died
# exactly there: the frame captured just before the click matches the link at
# 0.96, the FAILED frame 30 s later shows no splash over a finished
# C:\Program Files scan - the test's own success condition. The 26.9.29 run of
# the same sweep clicked three times too and differed only in which call the
# disappearance landed in: its exists(target, 5) tolerated it and moved on.
#
# Re-confirm in the match's own neighbourhood (a 172x31 search, not a screen
# sweep) so a splash that has already gone does not get a stray click put into
# whatever is underneath it - the results grid during a scan, but Explorer or
# the desktop once close_window has TreeSize on its way out, where a stray click
# plus the Alt+F4 below it closes the wrong window. Either way the answer is
# True, because what the callers actually ask is whether a splash was in the
# way: a splash on screen has already swallowed close_window's Alt+F4 whether or
# not this function is the thing that cleared it, and close_window re-sends the
# keystroke on True alone.
def dismiss_trial_splash(timeout=2):
    match = exists("continue-with-trial.png", timeout)
    if match is None:
        raised, match = raise_buried_splash()
        if not raised:
            return False
        if match is None:
            # Raised, but the link had not painted yet. A splash WAS in the way,
            # which is the question callers ask, and the next poll clicks it.
            return True
    around = Region(match.x - 6, match.y - 6, match.w + 12, match.h + 12)
    if around.exists("continue-with-trial.png", 0):
        click(match)
    return True

# The splash's own dark header - the TreeSize logo and wordmark. Unlike the
# link, this survives Explorer being raised over the splash, because Explorer
# lands below it. Measured with cv2 TM_CCOEFF_NORMED against the diagnostics of
# runs 34558812671 and 34558810483: 0.989-1.000 wherever a splash exists, front
# or buried, in EITHER run, and 0.265-0.331 with no splash on screen. Cut from
# the lossless -fail.png capture rather than a step frame, which is JPEG.
SPLASH_BANNER = "splash-banner.png"

# Bring a splash that something else has been raised over back to the front.
#
# Returns (raised, link): whether a splash was found and raised, and its link's
# Match if it had painted in time. Those are two different answers and the
# caller needs both. Probe run 34635346644 is why: the banner click raised the
# splash correctly - the frame two steps later shows the whole splash back over
# Explorer with the link readable - but the link was not findable until
# somewhere between 4 and 8 s after the click, so a single Match return would
# have been None and reported "no splash was in the way". That is the wrong
# answer for close_window, which re-sends its swallowed Alt+F4 on True alone.
#
# This is the gap that App Tests run 34558812671 fell into and that the comment
# here used to say could not be closed. Chain: the dismissing click at
# L[726,819] lands inside the Explorer window's rectangle, so when the splash
# goes out from under it the click falls through to Explorer and raises it over
# the replacement splash. From there the link is covered, the full-screen search
# above finds nothing and never clicks, and the same buried splash still clips
# TreeSize's address bar - so the gate below cannot match either. That run spent
# its whole 180 s budget on a screen that stopped changing: its step frames
# 38-45 and 46-52 are each indistinguishable from one another.
#
# The old note said the only part left visible was "a featureless strip of its
# dark banner". That was wrong - Explorer's top edge lands at y 205 and the
# banner spans y 90-300, so the whole logo and wordmark stay readable, at the
# same coordinates in every frame. See SPLASH_BANNER for the scores.
#
# Click the BANNER, not the owner. The splash is a separate top-level window, so
# clicking its own header raises it; activating TreeSize instead buries it,
# which is what deadlocked probe run 34544558910 and was reverted in 3d8dbd1.
# The header carries no controls, so the click does nothing but raise.
#
# Kept atomic the same way as the dismissal above: re-confirm the banner in its
# own neighbourhood and click the Match that exists() already returned, so a
# splash that has gone in the gap cannot take a stray click into Explorer or the
# desktop underneath it.
def raise_buried_splash():
    banner = exists(SPLASH_BANNER, 0)
    if banner is None:
        return (False, None)
    around = Region(banner.x - 6, banner.y - 6, banner.w + 12, banner.h + 12)
    if not around.exists(SPLASH_BANNER, 0):
        return (False, None)
    Debug.user("raise_buried_splash: splash found under something, raising it")
    click(banner)
    # 8 s rather than the 2 s that missed in 34635346644, which is comfortably
    # past the 4-8 s that run measured. Returning without the link is still
    # handled, so this is a convenience and not something correctness rests on.
    link = exists("continue-with-trial.png", 8)
    Debug.user("raise_buried_splash: link reachable after raising = %s" % link)
    return (True, link)

# The band of the TreeSize window that holds its address bar, given the match
# for the ribbon button above it.
#
# program-files.png is a 197x26 crop of that address bar, and it also matches
# EXPLORER's own "Program Files" row - the hazard measured when this block was
# last touched (0.64-0.69 there, "too close to 0.7 to use as a vanish gate")
# and left in. App Tests run 34539364831 is that hazard going off: clicking the
# splash away raised Explorer over a splash that stayed up, and the gate then
# matched Explorer's row at (563,482) instead of the address bar the splash was
# still covering, so wait_for_scan returned believing the scan was on screen.
# The step frame puts that row at 0.694, under SikuliX's 0.7 only because the
# JPEG is lossy - on the uncompressed screen it matched.
#
# Both elements are chrome of the same window, so their offset is fixed however
# the window is placed: over five runs select-scan-target.png landed at
# (118,166) every time and the address bar at (190,252). The band below is
# generous around that - roughly 90 px of slack left, 110 right, 46 up and 48
# down - and still reaches only x 498 / y 326, well clear of the Explorer row.
def address_bar_band(window_match):
    return Region(window_match.x - 20, window_match.y + 40, 400, 120)

# Wait for a shell context menu launch to reach its scan of (target_image),
# dismissing the "Easily Getting Started!" trial splash on the way.
#
# The splash and the main window come up together, about half a minute after the
# launch on a cold container - which is exactly the ambient
# setAutoWaitTimeout(30) that a bare `if exists("continue-with-trial.png")`
# inherits. In App Tests run 34097555049 that exists() lost the race by a second
# or two, returned False, and the splash then appeared and covered the address
# bar, so the wait for the scan target failed 30 s later against an image the
# splash was sitting on top of. Poll the two together instead: the splash covers
# the address bar, so the target being readable is itself proof the splash is
# gone, whichever order the two windows arrive in.
#
# A splash that something else has been raised over used to spin this loop out
# to its full budget, because the dismissal could not see it. raise_buried_splash
# closes that: see its comment for why the banner, and not the owner window, is
# the thing to click.
#
# More time is NOT the fix here and the budget should not be raised to paper
# over it. In run 34558812671 the scan finished inside the first half-minute and
# the screen then did not change for the remaining 145 s - a deadlock has no
# slow path to wait out. The slowness in that run was real but upstream: the
# container launch behind the context menu took 62 s against the sibling run's
# 24 s, while the SikuliX steps around it ran at the same speed or faster. A
# slow launch buys more splash instances (six against the sibling's one), which
# is more chances to hit the fall-through click - not a longer scan.
#
# Searched inside the band rather than on the whole screen, which costs the
# per-poll step frame for the gate (Region.exists is a bound method, so the
# hooks in util - which patch module-level names - do not wrap it). The splash
# check in the loop is still a module-level exists(), so every round leaves a
# frame of the same screen a few seconds later and the loop stays visible in
# the diagnostics.
def wait_for_scan(target_image, timeout=180):
    band = address_bar_band(wait(TREESIZE_WINDOW, timeout))
    deadline = time.time() + timeout
    while time.time() < deadline:
        if band.exists(target_image, 5):
            return
        dismiss_trial_splash()
    # Say which of the two states this is. "TreeSize did not scan it" was
    # actively misleading in run 34558812671, where the scan had finished long
    # before the budget ran out and a splash nobody could reach was covering the
    # evidence - three separate triages started from the wrong end of the test.
    if exists(SPLASH_BANNER, 0):
        raise FindFailed("%s: a trial splash was still covering TreeSize's address bar after %d s"
                         % (target_image, timeout))
    raise FindFailed("%s: TreeSize did not scan it within %d s" % (target_image, timeout))

# Activate (window) if one was named, then ask it to close.
#
# Never while the trial splash is visible. The splash is a separate top-level
# window and it does NOT ride along with its owner: activating the main window
# puts the splash BEHIND it, where it still blocks the close and can no longer
# be seen or clicked. Probe run 34544558910 ended in exactly that deadlock -
# main window focused and frontmost over a finished scan, the splash's title
# strip and its "Continue with trial version" link just visible above and below
# it, and 180 s of Alt+F4 doing nothing. Leaving the splash on top instead
# costs nothing, because the splash handling in close_window's loop clears it
# and then re-sends the keystroke.
#
# Activation is a precaution rather than something a probe has exercised: with
# the gate restricted to TreeSize's own window the loop can in principle return
# while Explorer holds the foreground, and Alt+F4 would then close Explorer.
def send_close(window=None):
    if window and not exists("continue-with-trial.png", 0):
        util.activate_app_window(window, 1)
    type(Key.F4, Key.ALT)

# Close a TreeSize window and confirm it is gone before the test moves on.
#
# Alt+F4 sent to TreeSize while a scan is still running is not acted on until
# the scan finishes, and the reference the test waits for before closing -
# TreeSize's address bar - fills in when the scan STARTS, so the old
# wait("program-files.png") + wait(3) closed the window mid-scan. In App Tests
# run 34097578991 it was still up four seconds later and the right-click that
# followed found sikuli-folder.png in TreeSize's own title bar,
# "C:\Program Files\ - TreeSize (Administrator)" - the same text in the same
# font on the same white as the Explorer row the reference was cropped from,
# matching at 0.834 - so no shell context menu opened and the test died at the
# next image, three lines from the actual fault.
#
# So send Alt+F4 once and then wait the window out, clearing the splash if one
# turns up. A splash that arrives after the scan target became readable is what
# broke App Tests run 34269857819: the close went into the splash, which
# swallowed it, and the window then sat there for three minutes with the app
# responding normally behind it. Clearing a splash therefore means the keystroke
# was lost and has to be sent again - and that is the ONLY thing that re-sends
# it, because a splash on screen is itself proof TreeSize is still up.
#
# Re-sending on a timer instead is what broke run 34271577102: the second Alt+F4
# went out six seconds after the first, into the gap while TreeSize was still
# tearing down (the step frames put the anchor at 0.96 when it was checked and
# 0.34 two seconds later, when the keystroke went out), so Explorer took the
# foreground and closed instead, and the right-clicks that followed had no window
# to aim at.
#
# Alt+F4 goes to whatever is focused, and that is not always the window being
# closed: in run 34539364831 clicking the splash away raised Explorer, which
# does not cover TreeSize's address bar, so once the gate reads that bar the
# loop can hand a foreground Explorer to close_window. Alt+F4 would then close
# EXPLORER and leave the right-clicks that follow with no window - the same
# damage the 29d5a08 timer did. So callers that know which window they mean
# name it and it is activated before every keystroke.
#
# Only the main window is named. The Advanced File Search and Find Duplicate
# Files dialogs are separate top-level windows that come up focused and close
# on Alt+F4 today, and activating the MAIN window before closing one of those
# would close the wrong window.
#
# Polled with exists() rather than waitVanish() so each look leaves a step frame
# and a window that will not close is visible in the diagnostics.
def close_window(anchor, timeout=180, poll=5, window=None):
    deadline = time.time() + timeout
    send_close(window)
    while True:
        if dismiss_trial_splash(1):
            wait(1)
            send_close(window)
        if not exists(anchor, 1):
            return
        if time.time() >= deadline:
            break
        wait(poll)
    Debug.user("close_window: %s still on screen %d s after Alt+F4" % (anchor, timeout))
    raise FindFailed("%s: the window did not close" % anchor)

# Test of `turbo run`.
wait("license-prompt.png")
type(Key.F4, Key.ALT)
wait(5)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(os.path.join(util.start_menu, "TreeSize"), "TreeSize"))
wait("license-prompt.png")
click("license-ok.png")
wait(TREESIZE_WINDOW)
type("f", Key.ALT)
type("t")
click("directory.png")
click("desktop.png")
click("confirm-selection.png")
wait("edge-lnk.png")
wait(5)
# Close app
close_window(TREESIZE_WINDOW, window=TREESIZE_TITLE)

# Test shell context menu
run("explorer c:\\")
wait("sikuli-folder.png")
wait(2)
# Pin the folder row rather than re-finding it before every right-click: the
# first right-click selects the row, and the highlighted row no longer matches
# the reference (0.55) while the unselected "Program Files (x86)" row below it
# matches better (0.90), so a re-search silently walks down the list.
folder = find("sikuli-folder.png")

rightClick(folder)
click("treesize-context-menu.png")
wait_for_scan("program-files.png")
close_window(TREESIZE_WINDOW, window=TREESIZE_TITLE)

rightClick(folder)
click("adv-file-search.png")
wait("search-configuration.png")
wait(10)
close_window("search-configuration.png")

rightClick(folder)
click("find-files-context.png")
wait("basic-search.png")
wait(10)
close_window("basic-search.png")
wait(5)

# Check if the session terminates.
util.check_running()
