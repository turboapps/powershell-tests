script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(10)
util.pre_test()

# Test of `turbo run`.
# Exit with error code if the WebView2 layer is not working.
if exists("update-required.png"):
    sys.exit(1)
setAutoWaitTimeout(30)
wait("home_button.png")
wait(10)
click(Pattern("close_pbi.png").targetOffset(42,-1))
wait(5)
if exists(Pattern("red_x_click.png").targetOffset(42,1)):
    click(Pattern("red_x_click.png").targetOffset(42,1))
wait(5)

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Microsoft Power BI Desktop", "Power BI Desktop.lnk"))
# Exit with error code if the WebView2 layer is not working.
if exists("update-required.png"):
    sys.exit(1)
wait("home_button.png")
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()