script_path = os.path.dirname(os.path.abspath(sys.argv[0]))
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import subprocess
import urllib2
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test(no_min=True)

# resources\www\index.php prints MARKER (it computes the 42 itself), so the text
# appears only when PHP ran the page - a raw copy of the source does not contain it.
URL = "http://localhost:8000"
MARKER = "PHP Server Test 42"
www = os.path.abspath(os.path.join(script_path, os.pardir, "resources", "www"))

# Start php.exe (the image's default startup file) as the built-in web server.
# This launch is made here rather than by Executor.ps1's StandardTest because
# TryTurboApp always adds --network=test, which puts the container on a virtual
# network that the native browser cannot reach at localhost:8000. Without
# --network the server binds on the host's loopback.
subprocess.Popen("turbo " + util.try_verb() + " php/php --name=test --enable=usedllinjection,cachefileinfo"
                 " --disable-proxy-resolve-via-proxy -d" + util.read_extra() +
                 ' -- -S 127.0.0.1:8000 -t "' + www + '"')

# Test.
# The built-in server prints its "Development Server ... started" banner, but the
# console host and font differ between XVM versions (see the apache test), so wait
# for php.exe and then for the port to answer instead of matching the console.
for attempt in range(30):
    if "php.exe" in run('tasklist /NH /FI "IMAGENAME eq php.exe"'):
        break
    wait(2)
else:
    assert False, "php.exe did not start within 60 s"

body = None
for attempt in range(30):
    try:
        body = urllib2.urlopen(URL, timeout=5).read()
        break
    except Exception, e:
        Debug.user("%s not answering yet: %s" % (URL, e))
        wait(2)
assert body is not None, "%s did not answer within 60 s" % URL
Debug.user("%s returned: %s" % (URL, body))
assert MARKER in body, "%s did not return the PHP-generated page" % URL

# Open the page in the browser. index.php puts MARKER in the page <title>, and the
# browser shows the title in its window caption, so check the caption rather than
# a screenshot of the page.
run('explorer "' + URL + '"')
for attempt in range(30):
    titles = util.list_processes("msedge.exe").values()
    if any(MARKER in title for title in titles):
        break
    wait(2)
else:
    assert False, "the browser did not show %s (window titles: %s)" % (MARKER, titles)
wait(5)
util.close_app("Edge")
wait(5)
run("turbo stop test")
wait(10)

# Check if the session terminates.
util.check_stopped("test")
