script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
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
type('turbo try postgresql/postgresql --using=pgvector/pgvector --startup-file=cmd --working-dir=C:\pgsql --mount C:\pg-data --name="test"' + Key.ENTER)
wait(10)
setAutoWaitTimeout(60)
wait("pgsql_ready.png")
click("pgsql_ready.png")
type("run-postgre-sql.bat" + Key.ENTER)
wait("pgsql_db_ready.png")
type("c", Key.CTRL)
wait("pgsql_terminate_batch.png")
type("y" + Key.ENTER)
type("cd C:\pgsql" + Key.ENTER)
type("pg_ctl start" + Key.ENTER)
wait("pgsql_started.png")
type("psql" + Key.ENTER)
wait("pgsql_password.png")
type("postgres" + Key.ENTER)
wait("pgsql_console.png")

# pgsql commands and pgvector.
type("CREATE EXTENSION vector;" + Key.ENTER)
wait("pgsql_result_1.png")
type("CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));" + Key.ENTER)
wait("pgsql_result_2.png")
type("INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');" + Key.ENTER)
wait("pgsql_result_3.png")
type("SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;" + Key.ENTER)
wait("pgsql_result_4.png")

# Check if the session terminates.
type("\q")
type("c", Key.CTRL)
type(Key.F4, Key.ALT)
run("turbo stop test")
wait(20)
assert("test" not in run("turbo sessions"))