# The tests for powerbi/powerbi and powerbi/powerbirs are the same except for the test file path.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(90)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait("home_button.png",60)
wait(10)
click(Pattern("close_pbi.png").targetOffset(42,-1))
wait(5)
if exists(Pattern("red_x_click.png").targetOffset(42,1)):
    click(Pattern("red_x_click.png").targetOffset(42,1))
wait(5)

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.desktop, "Power BI Desktop"))
wait("home_button.png",60)
click("sign_in.png")
wait("sign_in_email.png")
type(username)
type(Key.ENTER)
wait("sign_in_email_microsoft.png")
type(username)
type(Key.ENTER)
wait("sign_in_password.png")
type(password)
type(Key.ENTER)
wait("yes-all-apps.png")
click("yes-all-apps.png")
if exists("sign_in_went_wrong.png"):
    click("sign_in_continue.png")
else:
    wait("sign_in_all_set.png")
    click("sign_in_done.png")
wait(5)
if exists(Pattern("collaborate_prompt.png").targetOffset(174,-36)):
    click(Pattern("collaborate_prompt.png").targetOffset(174,-36))

# Basic operations.
setAutoWaitTimeout(60)
click("excel-data.png")
if exists("dark-mode-prompt.png", 15):
    click(Pattern("dark-mode-prompt.png").targetOffset(247,-250))
wait("import_file_name.png")
type("C:\\Program Files\\Microsoft Power BI Desktop RS\\bin\\SampleData\\Financial Sample.xlsx")
type(Key.ENTER)
click(Pattern("import_financials.png").targetOffset(-41,-2))
click("import_load.png")
click(Pattern("data_financials.png").targetOffset(-40,2))
click(Pattern("data_details.png").targetOffset(-45,-14))
click(Pattern("data_details.png").targetOffset(-45,10))
wait(5)
click("menu_file.png")
click("export_button.png")
click("export_pdf.png")
wait("pdf-print.png")
closeApp("Edge")
wait(10)
click("transform_data.png")
click("close_apply.png")

# Check "help".
click("menu_help.png")
click("help_support.png")
wait("help_url.png")
closeApp("Edge")
wait(10)
type(Key.F4, Key.ALT)
click("close_no_save.png")
wait(20)

# Check if the session terminates.
util.check_running()