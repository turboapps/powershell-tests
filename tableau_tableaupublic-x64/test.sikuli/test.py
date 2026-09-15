script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

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

# ===========================================================================
# PROBE ONLY - DO NOT MERGE.
#
# Sabotage for the Ctrl+O retry. The real defect (run 35002822157) is a
# keystroke that never reaches the app: the click raised the window, the
# chord raced the activation and lost, and Tableau stayed on its start page.
# From the application's side that is indistinguishable from no key being
# sent at all - so the probe sends nothing. That reproduces the state exactly
# and, unlike a focus-steal, cannot itself leave stray input on screen.
#
#   1. the OLD line (a single wait, 30 s budget) dies when the chord is lost
#   2. the SHIPPED retry loop recovers from that same state, and needs a
#      second attempt to do it
# Asserted at the end so the run reaches both phases and then completes the
# rest of the test normally.
# ===========================================================================

# --- Phase 1: the old single-shot wait, with the chord lost ---------------
old_failed = False
try:
    wait("file_location.png", 30)   # no Ctrl+O sent: the chord "went nowhere"
except FindFailed:
    old_failed = True
Debug.user("PROBE 1 old path died with the chord lost: %s" % old_failed)

# --- Phase 2: the shipped retry loop, sabotaged on its first attempt ------
attempts_used = 0
opened = False
for attempt in range(3):
    attempts_used = attempt + 1
    if attempt > 0:
        type("o", Key.CTRL)         # attempt 0 sends nothing: sabotage
    if exists("file_location.png", 15):
        opened = True
        break
    Debug.user("PROBE 2 no dialog after attempt %d, refocusing" % attempts_used)
    start_page = exists("tableau-open.png", 5)
    if start_page:
        click(start_page)
Debug.user("PROBE 2 retry loop opened the dialog: %s after %d attempt(s)" % (opened, attempts_used))

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
wait("workbook-open.png", 120)

# Switch to the Product Drilldown dashboard. The workbook opens on Overview,
# whose "Monthly Sales by Product Category" pane carries its own white-on-white
# "Furniture" row label on the right-hand side. Tableau needs several seconds to
# repaint this dashboard on a loaded VM, so without an anchor the search below
# matches that label on the dashboard we are leaving and clicks the wrong place.
# Wait for a caption that exists only here, and keep the search in the left-hand
# column where this dashboard's row headers live so the Overview label can never
# win even mid-repaint.
click("product-tab.png")
wait("product-drilldown.png", 120)
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
Debug.user("PROBE SUMMARY old_failed=%s opened=%s attempts=%d" % (old_failed, opened, attempts_used))
assert old_failed,     "SABOTAGE DID NOT REPRODUCE: the old single-shot wait survived a lost chord"
assert opened,     "FIX BROKEN: the retry loop never opened the Open dialog"
assert attempts_used >= 2,     "PROBE INCONCLUSIVE: the dialog opened on the sabotaged attempt that sent nothing"
Debug.user("PROBE PASSED: lost chord kills the old line, the retry loop recovers on attempt %d" % attempts_used)
