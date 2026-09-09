# The tests for nodejs/nodejs, nodejs/nodejs-lts and their arm64 variants are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test(no_min=True)

# The container console does not necessarily own the keyboard when the test
# starts - see util.focus_console - so take it before typing anything.
util.focus_console("node-cmd-prompt.png")

# Test cpp nodejs project.
#
# One chained command rather than five typed lines with a blind sleep after each.
# Those sleeps could neither reliably wait long enough nor tell whether a step
# had finished: on a loaded pool VM MSBuild was still linking addon.node when
# the test gave up (App Tests run 34097555049), and when `node-gyp configure`
# died early the test went on to run `node-gyp build` and `node index.js`
# anyway and failed three steps later on a missing addon (run 34295107851).
# cmd's && does the sequencing and the checking: nothing starts until the
# previous step has exited 0, a step that fails leaves its own error as the last
# thing on screen rather than two cascading follow-on failures, and one wait on
# the real end state replaces the four sleeps. The budget is several times the
# slowest npm install + node-gyp configure + MSBuild link seen on the pool.
type('cd my-node-cpp-app'
     ' && npm install node-addon-api@8'
     ' && npx --yes node-gyp configure'
     ' && npx --yes node-gyp build'
     ' && node index.js' + Key.ENTER)
wait("indexjs-result.png", 600)

# Test standard nodejs project.
type('node ..\my-node-app\\app.js' + Key.ENTER)
wait("server-running.png")
run('explorer "http://localhost:3000"')
wait("localhost.png")
wait(5)
util.close_app("Edge")
wait(5)
os.system('cmd /c taskkill /f /im "vctip.exe" /t')
run("turbo stop test")
wait(10)

# Check if the session terminates.
util.check_stopped("test")
