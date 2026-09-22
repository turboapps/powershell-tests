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
# Let Tableau finish its own exit before the session is stopped.
#
# Same change, same reason, as tableau_tableaureader-x64: this is the only close
# in the test that a `turbo stop` follows, Tableau's shutdown spawns
# `sc  stop "FlexNet Licensing Service 64"` on its way out, and a stop issued
# while that teardown is still running creates the child into a container that is
# already unloading. Under xvm 26.9.x such a child comes up with a completely
# unbound import table and dies with c0000005 EXECUTE at an address that is in no
# module (VM-2896, a product defect tracked with its own standalone repro; this
# only stops the test manufacturing the race).
#
# This app is where the defect was first root-caused: App Tests 35002798650,
# 35002810972 and 35022008056 on xvm 26.9.47 each staged an `sc.exe` dump with a
# clean, complete SikuliX log, failed by the crash-dump gate alone.
#
# The A/B was measured on the reader test, which drives the same shutdown through
# its licence prompt: 5/20 cycles wrote an sc.exe dump with the stop racing the
# exit and 0/20 with the stop issued after the process had gone (branch
# probe-tableau-turbostop-race, 5 App Tests runs on xvm 26.9.48, Fisher one-sided
# p = 0.024). Wait on the process rather than on the session, as
# autodesk_dwgtrueview does for the same reason.
util.wait_process_gone("tabpublic.exe", 120)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Tableau Public"))

# Basic operations.
wait("tableau-open.png",120)
click("tableau-open.png")

# Ctrl+O is sent immediately after a click whose only job is to raise the
# window, and on a loaded VM the activation and the chord race each other:
# run 35002822157 timed out on file_location.png with Tableau still sitting
# on its start page, so the keystroke had gone nowhere. Sending it again is
# safe only while the dialog is genuinely absent, so check the outcome and
# re-assert the focus before each retry rather than trusting either one.
for attempt in range(3):
    type("o", Key.CTRL)
    if exists("file_location.png", 15):
        break
    Debug.user("Ctrl+O did not open the Open dialog (attempt %d of 3)" % (attempt + 1))
    start_page = exists("tableau-open.png", 5)
    if start_page:
        click(start_page)
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