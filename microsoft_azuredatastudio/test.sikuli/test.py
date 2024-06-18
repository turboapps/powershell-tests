script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# close the alert for SQL Server Express.
util.close_firewall_alert()

# Test of `turbo run`.
App().focus("Azure Data Studio")
wait("ads_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Azure Data Studio", "Azure Data Studio.lnk"))
wait("ads_window.png")

# Basic operations.
click("create_connection.png")
if exists("privacy.png"):
    click(Pattern("privacy.png").targetOffset(206,-32))
click(Pattern("connection_type.png").targetOffset(62,20))
wait(2)
click(Pattern("connection_string.png").targetOffset(52,0))
type("Server=localhost;Database=master;Trusted_Connection=True;" + Key.ENTER)
click("connection_trust.png")

click(Pattern("query_options.png").targetOffset(-46,2))

wait("query_window.png")
type("CREATE DATABASE TestDB;")
click(Pattern("query_run.png").targetOffset(-23,0))
wait("query_result_1.png")
type("a", Key.CTRL)
type(Key.DELETE)

wait("query_window.png")
type("""USE TestDB;
CREATE TABLE Employees (
EmployeeID INT PRIMARY KEY,
FirstName VARCHAR(50),
LastName VARCHAR(50),
Age INT""")
click(Pattern("query_run.png").targetOffset(-23,0))
wait("query_result_1.png")
type("a", Key.CTRL)
type(Key.DELETE)

wait("query_window.png")
type("""INSERT INTO Employees (EmployeeID, FirstName, LastName, Age) VALUES
(1, 'John', 'Doe', 30),
(2, 'Jane', 'Smith', 25),
(3, 'David', 'Johnson', 35""")
click(Pattern("query_run.png").targetOffset(-23,0))
wait("query_result_2.png")
type("a", Key.CTRL)
type(Key.DELETE)

wait("query_window.png")
type("SELECT * FROM Employees;")
click(Pattern("query_run.png").targetOffset(-23,0))
wait("query_result_3.png")

# Check "help".
click(Pattern("menu.png").targetOffset(57,0))
click("menu_help.png")
click(Pattern("open_website.png").targetOffset(-33,46))
util.close_firewall_alert()
wait("help_url.png")
closeApp("Edge")
wait(10) # Wait for the complete close of the firewall alert.
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()