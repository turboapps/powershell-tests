script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# ===========================================================================
# PROBE ONLY - DO NOT MERGE.
#
# Sabotage for the fix in PR #214. The production failure (applab run
# 34873394316) was a race: the Product Drilldown dashboard had not repainted
# yet, so furniture.png matched the Overview dashboard's own "Furniture" row
# label at (1107,646) and every later click went to the wrong place.
#
# A race cannot be scheduled, so this probe CAUSES it: it matches
# furniture.png while Overview is still up, THEN clicks the Product tab and
# waits for the repaint to finish, THEN delivers the clicks at the stale
# coordinates. That is the production sequence with the race pinned to its
# losing outcome - matched on the old screen, clicked on the new one.
#
# An earlier revision of this probe simply never clicked the Product tab and
# asserted the old path would fail on a stationary Overview. It did NOT fail
# (run 34910248009): the Overview's "Furniture" IS a real field header, so
# right-clicking it opens a header menu that does contain "Keep only". The
# old test could therefore pass while filtering the WRONG dashboard - a
# vacuous pass - which is a second reason the anchor is needed. The repaint
# between match and click is the ingredient that turns it into a failure.
#
# Phases:
#   1. the decoy is real, reachable, and on the RIGHT-hand side of the screen
#   2. BOTH guards the fix adds reject the Overview screen
#   3. with the repaint forced in between, the OLD path dies with the
#      production signature (keep-only.png FindFailed)
#   4. the FIXED path succeeds on the real Product Drilldown
# Everything is asserted at the end so the run reaches all four phases.
# ===========================================================================

# Launch and open the workbook - unchanged from the real test.
wait("tableau-open.png",120)
click("tableau-open.png")
type(Key.F4, Key.ALT)
run("turbo stop test")
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Tableau Public"))
wait("tableau-open.png",120)
click("tableau-open.png")
type("o", Key.CTRL)
wait("file_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "US_Superstore_10.0.twbx"))
type(Key.ENTER)
wait("workbook-open.png")

headers = Region(0, 0, SCREEN.getW() // 2, SCREEN.getH())

# --- Phase 1: the decoy is real, and it is on the right-hand side ----------
decoy = exists("furniture.png", 10)
decoy_mid = decoy and (decoy.x + decoy.w // 2, decoy.y + decoy.h // 2)
Debug.user("PROBE 1 decoy on Overview: centre=%s score=%s (run 34873394316 clicked L[1107,646])"
           % (decoy_mid, decoy and round(decoy.getScore(), 3)))

# --- Phase 2: both guards the fix adds reject this screen -----------------
anchor_here = exists("product-drilldown.png", 5)
scoped_here = headers.exists("furniture.png", 5)
Debug.user("PROBE 2 on Overview: anchor=%s (want None)  left-half furniture=%s (want None)"
           % (anchor_here, scoped_here))

# --- Phase 3: SABOTAGE - force the repaint between match and click --------
# The match above was made against Overview. Now let the Product Drilldown
# paint, then deliver the old path's clicks at those stale coordinates, the
# way the real run did. On the new layout (1107,646) is empty space inside a
# worksheet container, so Tableau opens the dashboard-item menu and
# keep-only.png is never found.
click("product-tab.png")
wait("product-drilldown.png", 120)
old_path_failed = False
old_path_error = None
try:
    click(decoy)
    rightClick(Location(decoy_mid[0], decoy_mid[1] + 13))  # production hit L[1110,659]
    click("keep-only.png")
except FindFailed:
    old_path_failed = True
    old_path_error = str(sys.exc_info()[1]).splitlines()[0]
Debug.user("PROBE 3 old path FindFailed as in production: %s (%s)"
           % (old_path_failed, old_path_error))
type(Key.ESC)
wait(2)

# --- Phase 4: the fixed path works on the real dashboard ------------------
anchor_there = exists("product-drilldown.png", 120)
Debug.user("PROBE 4 anchor on Product Drilldown: %s score=%s"
           % (anchor_there and (anchor_there.x, anchor_there.y),
              anchor_there and round(anchor_there.getScore(), 3)))
header = headers.wait("furniture.png")
Debug.user("PROBE 4 header found in left half at centre=(%d,%d) score=%s"
           % (header.x + header.w // 2, header.y + header.h // 2, round(header.getScore(), 3)))
click(header)
rightClick(header)
keep_only = exists("keep-only.png", 10)
Debug.user("PROBE 4 header menu opened: %s" % (keep_only is not None))
if keep_only:
    click(keep_only)
    fixed_ok = exists("keep-only-result.png", 30) is not None
else:
    fixed_ok = False
Debug.user("PROBE 4 fixed path reached keep-only-result: %s" % fixed_ok)

# --- Verdict --------------------------------------------------------------
assert decoy is not None, \
    "PROBE INCONCLUSIVE: no furniture.png match on Overview, sabotage did not set up the state"
assert decoy.x > SCREEN.getW() // 2, \
    "PROBE INCONCLUSIVE: decoy at x=%d is not on the right-hand side" % decoy.x
assert old_path_failed, \
    "SABOTAGE DID NOT REPRODUCE: the old path survived the decoy screen"
assert anchor_here is None, \
    "GUARD BROKEN: product-drilldown.png matched the Overview dashboard"
assert scoped_here is None, \
    "GUARD BROKEN: the left-half region still reached the decoy"
assert anchor_there is not None, \
    "FIX BROKEN: product-drilldown.png never appeared on the Product dashboard"
assert header.x < SCREEN.getW() // 2, \
    "FIX BROKEN: header matched outside the left half at x=%d" % header.x
assert fixed_ok, \
    "FIX BROKEN: the fixed path did not reach keep-only-result on the real dashboard"
Debug.user("PROBE PASSED: decoy reproduced the production failure, both guards rejected it, fixed path worked")
