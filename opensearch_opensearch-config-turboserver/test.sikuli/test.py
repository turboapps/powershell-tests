# The tests for opensearch/opensearch and opensearch/opensearch-config-turboserver are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import subprocess
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

# Minimize the sikulix console
if exists("sikulix-console.png",15):
    click("sikulix-console.png")
    wait(2)
    type(Key.DOWN, Key.WIN)

# Warmup.
wait(30)
wait(Pattern("opensearch_ready.png").similar(0.80),90)

# Test.
subprocess.Popen('turbo try base --using=isolate-edge-wc -n=edge --enable=usedllinjection --network=test --isolate=merge --startup-file="C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" -d -- http://localhost:9200/_cat/indices?v')
App().focus("Edge")
wait("green-open.png",10)

putfile = os.path.join(script_path, os.pardir, "resources", "put.bat")
subprocess.Popen("turbo try base -n=curl --network=test --isolate=merge --startup-file=cmd -d -- /C " + putfile)
wait(5)
App().focus("Edge")
wait(3)
type("d", Key.ALT)
paste("localhost:9200/_snapshot/cve_backup")
type(Key.ENTER)
wait("cve-backup.png")
type(Key.F4, Key.ALT)

run("turbo stop test")
wait(10)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))
