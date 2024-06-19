script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(include_path, os.pardir, "secrets.txt"))
domain = credentials.get("Domain")
api_key = credentials.get("APIKey")

# Setup.
click("runas_password.png")
type("password" + Key.ENTER)
wait("runas_ready.png")
type("turbo config --domain=" + domain + Key.ENTER)
if api_key:
    type("turbo login --api-key=" + api_key + Key.ENTER)
type('turbo run postgresql/postgresql --startup-file=cmd --working-dir=C:\pgsql --mount C:\pg-data --name="test"' + Key.ENTER)
wait(10)
wait("pgsql_ready.png",90)
click("pgsql_ready.png")
type("run-postgre-sql.bat" + Key.ENTER)
wait("pgsql_db_ready.png",90)
type("c", Key.CTRL)
wait("pgsql_terminate_batch.png")
type("y" + Key.ENTER)
type("cd C:\pgsql" + Key.ENTER)
type("pg_ctl start" + Key.ENTER)
wait("pgsql_started.png",90)
type("psql" + Key.ENTER)
wait("pgsql_password.png")
type("postgres" + Key.ENTER)
wait("pgsql_console.png",90)

# pgsql commands.
type("CREATE TABLE Employee (EmployeeID INT PRIMARY KEY, FirstName VARCHAR(50), LastName VARCHAR(50), Age INT);" + Key.ENTER)
wait("pgsql_result_1.png")
type("INSERT INTO Employee (EmployeeID, FirstName, LastName, Age) VALUES (1, 'John', 'Doe', 30), (2, 'Jane', 'Smith', 25), (3, 'David', 'Johnson', 35);" + Key.ENTER)
wait("pgsql_result_2.png")
type("SELECT * FROM Employee;" + Key.ENTER)
wait("pgsql_result_3.png")

# Chcek "help".
type("help" + Key.ENTER)
wait("pgsql_help.png")

# Check if the session terminates.
type("\q")
type("c", Key.CTRL)
type("exit")
type(Key.ENTER)
run("turbo stop test")
