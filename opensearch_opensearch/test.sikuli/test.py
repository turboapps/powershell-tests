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

# Warmup.
wait(30)
wait(Pattern("opensearch_ready.png").similar(0.80),90)

# Test.
subprocess.Popen('turbo ' + util.try_verb() + ' base --using=isolate-edge-wc -n=edge --enable=usedllinjection --network=test --isolate=merge --startup-file="C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe" -d' + util.read_extra() + ' -- http://localhost:9200/_cat/indices?v')
# The launch above is asynchronous, so this wait has to cover the container
# being created, Edge cold-starting and only then the page being fetched: the
# step frame taken as the wait begins shows no Edge window at all, in a passing
# run as much as a failing one. 10 s did not cover that on a loaded CI VM --
# App Tests 34097555049 gave up with the tab still reading "Loading...", and
# 34097578991 rendered the row in the gap between SikuliX's last poll and the
# FindFailed (the reference matches that run's own failure screenshot exactly).
# A bare App().focus("Edge") here also runs before Edge exists, so it is a
# silent no-op and nothing retries it. Poll and re-focus instead.
if not util.focus_and_wait("Edge", "green-open.png", attempts=9, poll=10):
    wait("green-open.png")  # still absent: fail with the usual FindFailed

putfile = os.path.join(script_path, os.pardir, "resources", "put.bat")
subprocess.Popen("turbo " + util.try_verb() + " base -n=curl --network=test --isolate=merge --startup-file=cmd -d" + util.read_extra() + " -- /C " + putfile)
# Give the PUT above a head start, then navigate -- verified, because the console
# that PUT runs in can still be on top of Edge when the chord is sent.
wait(5)
util.navigate_browser("Edge", "localhost:9200/_snapshot/cve_backup", "cve-backup.png")
type(Key.F4, Key.ALT)

run("turbo stop test")
wait(10)

# Check if the session terminates.
util.check_stopped("test")
