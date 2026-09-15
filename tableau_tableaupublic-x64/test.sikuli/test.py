script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

import time

# ===========================================================================
# PROBE ONLY - DO NOT MERGE.
#
# Measures the two durations PR #214 makes assumptions about, because a
# budget change that is never measured is a guess (see the azuredatastudio
# fix, where idle-pool launches took 12-16 s and only a loaded probe showed
# the real 122 s):
#   A. Enter -> workbook-open, which run 34910120439 blew past at 30 s and
#      the fix now allows 120 s.
#   B. Product tab click -> Product Drilldown painted, which is the race
#      window the anchor closes. The production run was still showing the
#      old dashboard ~6 s in.
# Both are given a deliberately huge ceiling so the probe reports a number
# instead of dying, and both are asserted against the shipped budgets at the
# end so a run that blows them fails loudly.
# ===========================================================================

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("tableau-open.png",120)
click("tableau-open.png")
type(Key.F4, Key.ALT)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Tableau Public"))

# Basic operations.
wait("tableau-open.png",120)
click("tableau-open.png")
type("o", Key.CTRL)
wait("file_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "US_Superstore_10.0.twbx"))
type(Key.ENTER)

# US_Superstore_10.0.twbx is a packaged workbook with several dashboards
# (the Product one alone carries 4254 marks), and Tableau builds it in
# stages: it connects the data sources first and only then materialises the
# sheets and retitles the window. On a loaded pool VM that outruns the 30 s
# setAutoWaitTimeout - run 34910120439 timed out here with the load visibly
# still in progress, the Data pane already listing the workbook's three data
# sources while the window was still "Book1" on an empty Sheet 1. The two
# launch waits above already allow 120 s; this one was the only wait in the
# file left on the default.
_t0 = time.time()
wait("workbook-open.png", 300)
load_secs = time.time() - _t0
Debug.user("PROBE A workbook load: %.1f s (old budget 30 s, shipped budget 120 s)" % load_secs)

# Switch to the Product Drilldown dashboard. The workbook opens on Overview,
# whose "Monthly Sales by Product Category" pane carries its own white-on-white
# "Furniture" row label on the right-hand side. Tableau needs several seconds to
# repaint this dashboard on a loaded VM, so without an anchor the search below
# matches that label on the dashboard we are leaving and clicks the wrong place.
# Wait for a caption that exists only here, and keep the search in the left-hand
# column where this dashboard's row headers live so the Overview label can never
# win even mid-repaint.
click("product-tab.png")
_t1 = time.time()
wait("product-drilldown.png", 300)
repaint_secs = time.time() - _t1
Debug.user("PROBE B Product Drilldown repaint: %.1f s (the race window the anchor closes)" % repaint_secs)
headers = Region(0, 0, SCREEN.getW() // 2, SCREEN.getH())

# Filter the crosstab down to the Furniture category. Locate the row header
# once and reuse the match, so a retry cannot drift onto the second "Furniture"
# label further down the dashboard.
header = headers.wait("furniture.png")
keep_only = None
for attempt in range(3):
    click(header)
    rightClick(header)
    keep_only = exists("keep-only.png", 10)
    if keep_only:
        break
    # A right-click that lands beside the header opens the dashboard-item menu
    # ("Go to Sheet", "Remove from Dashboard") instead of the header menu.
    # Dismiss whatever opened and aim again.
    type(Key.ESC)
if not keep_only:
    keep_only = wait("keep-only.png")
click(keep_only)
wait("keep-only-result.png")

# Check "help".
type(Key.F1)
wait("help_url.png")
util.close_app("Edge")
wait(10) # Wait for the complete close of the firewall alert.
type(Key.F4, Key.ALT)
if exists("save-changes-prompt.png"):
    click(Pattern("save-changes-prompt.png").targetOffset(14,27))
wait(20)

# Check if the session terminates.
util.check_running()
Debug.user("PROBE SUMMARY workbook_load=%.1fs repaint=%.1fs" % (load_secs, repaint_secs))
assert load_secs < 120,     "workbook load %.1f s exceeded the shipped 120 s budget" % load_secs
assert repaint_secs < 120,     "repaint %.1f s exceeded the anchor's 120 s budget" % repaint_secs
