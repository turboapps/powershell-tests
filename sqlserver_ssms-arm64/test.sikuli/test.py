script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

# Test of `turbo run`.
deadline = time.time() + 90
while not exists("ssms_window.png", 0):
    if time.time() > deadline:
        raise Exception("SSMS window did not appear within 90 seconds")
    App("Microsoft SQL Server Management Studio").focus()
    time.sleep(2)
click("ssms-close-x.png")
type(Key.ENTER)

folder_path = util.get_shortcut_path_by_prefix(util.start_menu, "Microsoft SQL Server Tools")
run("explorer " + util.get_shortcut_path_by_prefix(folder_path, "SQL Server Management Studio"))
wait(30)
wait("ssms_window.png",90)
click("ssms_window.png")

# Basic operations.
click("server_name.png")
type("localhost")
click("security.png")
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
type(Key.F1)
wait(15)
App().focus("Edge")
wait("help_url.png",30)
util.close_app("Edge")
wait(10)
type(Key.F4, Key.ALT)
click("save.png")

# Check if the session terminates.
util.check_running()