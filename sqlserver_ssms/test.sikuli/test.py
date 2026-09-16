script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

# Test of `turbo run`.
wait("ssms_window.png",90)
App("Microsoft SQL Server Management Studio").focus()
wait(3)
click("ssms-close-x.png")
type(Key.ENTER)

folder_path = util.get_shortcut_path_by_prefix(util.start_menu, "Microsoft SQL Server Tools")
run("explorer " + util.get_shortcut_path_by_prefix(folder_path, "SQL Server Management Studio"))
wait("ssms_window.png",90)
wait(3)
click("ssms_window.png")

# Basic operations.
wait("server_name.png",90)
wait(3)
click("server_name.png")
type("localhost")
click("security.png")
type(Key.ENTER)
wait("db_loaded.png")

# SSMS 22 opens its "What's new" document a couple of seconds after the
# connection completes, and can bring it back to the front later - over the
# query editor. Close it here; util.ssms_run_query covers it if it returns.
# PROBE ONLY: left out so the What's new document is still around to steal with.
# util.ssms_close_whats_new()

type("n", Key.CTRL)

util.ssms_run_query("CREATE DATABASE TestDB;", "query_result_1.png")
util.ssms_clear_query()

util.ssms_run_query("""USE TestDB;
CREATE TABLE Employees (
EmployeeID INT PRIMARY KEY,
FirstName VARCHAR(50),
LastName VARCHAR(50),
Age INT);""", "query_result_1.png")
util.ssms_clear_query()

util.ssms_run_query("""INSERT INTO Employees (EmployeeID, FirstName, LastName, Age) VALUES
(1, 'John', 'Doe', 30),
(2, 'Jane', 'Smith', 25),
(3, 'David', 'Johnson', 35);""", "query_result_2.png")
util.ssms_clear_query()

util.ssms_run_query("SELECT * FROM Employees;", "query_result_3.png")

# Check "help".
type(Key.F1)
wait(20)
App().focus("Edge")
wait("help_url.png",120)
util.close_app("Edge")
wait(10)
type(Key.F4, Key.ALT)
click("save.png")

# Check if the session terminates.
util.check_running()