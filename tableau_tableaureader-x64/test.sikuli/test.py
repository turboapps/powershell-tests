script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Test of `turbo run`.
wait("tableau_reg.png", 60)
click(Pattern("tableau_reg.png").targetOffset(-289,0))
type(Key.F4, Key.ALT)
click(Pattern("tableau_reg_exit.png").targetOffset(-139,10))
click(Pattern("tableau_reg_exit.png").targetOffset(99,52))
# Let Tableau finish its own exit before the session is stopped.
#
# This is the only close in the test that a `turbo stop` follows, and it is the
# only place that has ever produced a crash dump. Tableau's shutdown spawns
# `sc  stop "FlexNet Licensing Service 64"` twice, inside the last ~1.5 s of
# tabreader.exe's life - the VM logs from App Tests 35775110559 put the
# NtCreateUserProcess in tabreader.exe's own xclog, not in any Turbo process. So
# a stop issued while that teardown is still running creates those children into
# a container that is already unloading. Under xvm 26.9.x such a child comes up with a completely
# unbound import table - every IAT slot still holds the on-disk RVA of its own
# IMAGE_IMPORT_BY_NAME record - and dies on its first call through a thunk with
# c0000005 EXECUTE at an address that is in no module. That is VM-2896, a product
# defect tracked with its own standalone repro; this only stops the test
# manufacturing the race.
#
# SikuliX never notices: the script passes end to end and the job is failed by
# the crash-dump gate. App Tests 35678863980 (reader, sc.exe.6080.dmp, fault at
# 0x13346 = "__C_specific_handler") and 35002798650 / 35002810972 / 35022008056
# (public, xvm 26.9.47) all look like that.
#
# Measured on branch probe-tableau-turbostop-race, 5 App Tests runs x 8 cycles on
# xvm 26.9.48, the arms alternating inside each job:
#
#     stop-races (this test today)  5/20 cycles wrote an sc.exe dump, 7/20 any
#     stop-after (this change)      0/20                            , 0/20
#
# Fisher one-sided p = 0.024 on sc.exe, p = 0.0042 on any dump. The two extra
# dumps under stop-races were `conhost.exe --headless` - sc.exe's own console
# host, killed by the same unbound IAT (hint 0x0018 "GetSystemTimeAsFileTime",
# reached from _security_init_cookie).
#
# The application exits ~2 s after the close (the probe measured 2-6 s over 20
# cycles), so this normally costs nothing. Wait on the process rather than on the
# session, as autodesk_dwgtrueview does for the same reason.
util.wait_process_gone("tabreader.exe", 120)
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Tableau Reader"))
wait("tableau_reg.png", 60)
click(Pattern("tableau_reg.png").targetOffset(-289,0))
paste("Sandy")
type(Key.TAB)
paste("Sandbox")
type(Key.TAB)
paste("Spoon")
type(Key.TAB)
paste("sandy@email.com")
click(Pattern("tableau_reg_country.png").targetOffset(110,9))
click("tableau_reg_country_dropdown.png")
click(Pattern("tableau_reg_state.png").targetOffset(65,9))
click("tableau_reg_state_dropdown.png")
click("tableau_reg_size.png")
click("tableau_reg_size_dropdown.png")
type(Key.ENTER)
wait("tableau_reg_completed.png")
type(Key.ENTER)

# Basic operations.
wait("tableau_window.png")
type("o", Key.CTRL)
wait("file_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "US_Superstore_10.0.twbx"))
type(Key.ENTER)
wait("workbook-open.png")
click("product-tab.png")
click("furniture.png")
rightClick("furniture-selected.png")
click("keep-only.png")
wait("keep-only-result.png")
type("p", Key.CTRL)
wait("print_window.png")
type(Key.ESC)
wait("keep-only-result.png")

# Check "help".
type(Key.F1)
wait("help_url.png")
util.close_app("Edge")
wait(10) # Wait for the complete close of the firewall alert.
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()