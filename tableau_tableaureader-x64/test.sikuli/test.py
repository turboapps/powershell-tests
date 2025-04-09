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
run("turbo stop test")

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Tableau Reader"))
wait("tableau_reg.png", 60)
click(Pattern("tableau_reg.png").targetOffset(-289,0))
type("Sandy" + Key.TAB)
type("Sandbox" + Key.TAB)
type("Spoon" + Key.TAB)
type("sandy@email.com")
click(Pattern("tableau_reg_country.png").targetOffset(110,9))
click(Pattern("tableau_reg_country_dropdown.png").targetOffset(-8,-24))
click(Pattern("tableau_reg_state.png").targetOffset(65,9))
click(Pattern("tableau_reg_state_dropdown.png").targetOffset(-7,-25))
click("tableau_reg_size.png")
click(Pattern("tableau_reg_size_dropdown.png").targetOffset(-8,-22))
type(Key.ENTER)
wait("tableau_reg_completed.png")
type(Key.ENTER)

# Basic operations.
wait("tableau_window.png")
type("o", Key.CTRL)
wait("file_location.png")
type(os.path.join(script_path, os.pardir, "resources", "US_Superstore_10.0.twbx") + Key.ENTER)
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
closeApp("Edge")
wait(10) # Wait for the complete close of the firewall alert.
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()