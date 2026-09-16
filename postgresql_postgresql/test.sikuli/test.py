script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import time
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(include_path, os.pardir, "secrets.txt"))
domain = credentials.get("Domain")
api_key = credentials.get("APIKey")

# Read extra parameters from the extra.txt.
with open(os.path.join(script_path, os.pardir, "extra.txt"), "r") as file:
    extra = file.read().replace("\n", "")

# Setup.
wait("runas_password.png")
click("runas_password.png")
wait(2)
paste("password")
wait(2)
type(Key.ENTER)
# PROBE ONLY - DO NOT MERGE.
# Ctrl+Esc opens the Start menu, which takes the foreground without covering
# the console's top-left prompt - the exact state run 35063730062 was in when
# the runas console was on screen but unfocused. Coordinate-free, and unlike
# Win+D it does not disturb the z-order.
type(Key.ESC, Key.CTRL)
wait(3)
# Take the keyboard from the console runas just opened, do not assume it.
#
# runas_ready.png is the child window's own "C:\Windows\System32>" prompt, so
# matching it proves that window exists and is painted - not that it owns the
# keyboard. In App Tests run 35063730062 (xvm 26.9.48) it came up topmost but
# never took the foreground: the taskbar button carried the inactive grey pill
# rather than the blue active underline from step frame 006 onward, and every
# paste and Enter after this line was discarded. The console still held a bare
# "C:\Windows\System32>" in the FAILED frame two minutes later, with not one
# of the four commands echoed, and the test died at pgsql_ready.png having done
# nothing at all. The same run on 26.9.47 shows the blue underline from frame
# 006 on and the commands land, so this is a focus race, not a build.
#
# focus_console clicks the prompt and confirms the window came forward before
# returning, so the first paste cannot be thrown away.
# PROBE ONLY: the pre-fix blind wait.
wait("runas_ready.png")
wait(2)
paste("turbo config --domain=" + domain)
wait(2)
type(Key.ENTER)
if api_key:
    wait(2)
    paste("turbo login --api-key=" + api_key)
    wait(2)
    type(Key.ENTER)
wait(5)
paste("turbo pull xvm")
wait(2)
type(Key.ENTER)
wait(10)
paste('turbo try postgresql/postgresql:16 --using=pgvector/pgvector --startup-file=cmd --working-dir=C:\pgsql --mount C:\pg-data --name="test" ' + extra)
wait(2)
type(Key.ENTER)
wait(10)
# Give the container prompt a budget that covers a cold image pull.
#
# The pipeline pre-pulls the tag under test (postgresql:18.6 today); this line
# asks for :16, which resolves to postgresql:16.4 - 987 MB - and pulls
# pgvector/pgvector on top of it, so on a VM whose cache holds neither, the
# whole download happens inside this wait. In App Tests run 35063712843 the
# FAILED frame catches it at "Pulling image postgresql:16.4 ... (55%; 544MB of
# 987MB)" when the 60 s expired; the run that passed on 2026-09-15 had the
# images cached and reached the prompt in 14 s. So the test was only ever
# passing on a warm cache.
#
# Retrying is not an option - re-issuing turbo try against an in-flight pull
# would make things worse - and there is no earlier outcome to check, so the
# budget is the lever here. 987 MB at the ~9 MB/s this run measured is ~110 s of
# download before pgvector, the tail of the turbo pull xvm above (still running
# 60 s after its Enter in that same run) and container startup; a pool VM
# sharing bandwidth with the rest of the suite can take several times that.
# 600 s is a ceiling, not a delay: the wait returns the moment the prompt
# appears, so a warm VM still costs the same 14 s it always did.
setAutoWaitTimeout(600)
pull_started = time.time()
wait("pgsql_ready.png")
Debug.user("container prompt ready %d s after turbo try" % (time.time() - pull_started))
setAutoWaitTimeout(60)
click("pgsql_ready.png")
wait(2)
paste("run-postgre-sql.bat")
wait(2)
type(Key.ENTER)
wait("pgsql_db_ready.png")
type("c", Key.CTRL)
wait("pgsql_terminate_batch.png")
type("y")
type(Key.ENTER)
wait(2)
paste("cd C:\pgsql")
wait(2)
type(Key.ENTER)
wait(2)
paste("pg_ctl start")
wait(2)
type(Key.ENTER)
wait("pgsql_started.png")
type("psql")
type(Key.ENTER)
wait("pgsql_password.png")
type("postgres")
type(Key.ENTER)
wait("pgsql_console.png")

# pgsql commands and pgvector.
paste("CREATE EXTENSION vector;")
wait(2)
type(Key.ENTER)
wait("pgsql_result_1.png")
paste("CREATE TABLE items (id bigserial PRIMARY KEY, embedding vector(3));")
wait(2)
type(Key.ENTER)
wait("pgsql_result_2.png")
paste("INSERT INTO items (embedding) VALUES ('[1,2,3]'), ('[4,5,6]');")
wait(2)
type(Key.ENTER)
wait("pgsql_result_3.png")
paste("SELECT * FROM items ORDER BY embedding <-> '[3,1,2]' LIMIT 5;")
wait(2)
type(Key.ENTER)
wait("pgsql_result_4.png")

# Check if the session terminates.
type("\q")
type("c", Key.CTRL)
wait(10)
type(Key.ENTER)
wait(5)
type("exit")
type(Key.ENTER)
run("turbo stop test")
wait(20)
util.check_stopped("test")
