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
wait(60)
App().focus("Microsoft SQL Server Management Studio")
wait("ssms_window.png")
run("turbo stop test")

# Launch the app.
folder_path = util.get_shortcut_path_by_prefix(util.start_menu, "Microsoft SQL Server Tools")
run("explorer " + util.get_shortcut_path_by_prefix(folder_path, "SQL Server Management Studio"))
wait(30)
wait("ssms_window.png", 60)

# Basic operations.
click("server_name.png")
type("localhost")
click(Pattern("security.png").targetOffset(-62,11))
type(Key.ENTER)
wait("db_loaded.png")
type("n", Key.CTRL)

wait("query_area.png")
type("CREATE DATABASE TestDB;" + Key.F5)
wait("query_result_1.png")
type("a", Key.CTRL)
type(Key.DELETE)

wait("query_area.png")
type("""USE TestDB;
CREATE TABLE Employees (
EmployeeID INT PRIMARY KEY,
FirstName VARCHAR(50),
LastName VARCHAR(50),
Age INT);""" + Key.F5)
wait("query_result_1.png")
type("a", Key.CTRL)
type(Key.DELETE)

wait("query_area.png")
type("""INSERT INTO Employees (EmployeeID, FirstName, LastName, Age) VALUES
(1, 'John', 'Doe', 30),
(2, 'Jane', 'Smith', 25),
(3, 'David', 'Johnson', 35);""" + Key.F5)
wait("query_result_2.png")
type("a", Key.CTRL)
type(Key.DELETE)

wait("query_area.png")
type("SELECT * FROM Employees;" + Key.F5)
wait("query_result_3.png")

# Check "help".
type(Key.F2, Key.CTRL + Key.ALT)
util.close_firewall_alert()
wait("help_url.png")
closeApp("Edge")
wait(10)
type(Key.F4, Key.ALT)
click(Pattern("save.png").targetOffset(70,116))
wait(30)

# Check if the session terminates.
util.check_running()