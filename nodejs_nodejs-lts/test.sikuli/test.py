script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Test cpp nodejs project
type('npm install -g node-gyp' + Key.ENTER)
wait(10)
type('cd my-node-cpp-app' + Key.ENTER)
wait(3)
type('node-gyp clean' + Key.ENTER)
wait(5)
type('node-gyp configure' + Key.ENTER)
wait(45)
type('node-gyp build' + Key.ENTER)
wait(15)
type('node index.js' + Key.ENTER)
wait(5)
wait("indexjs-result.png")

# Test standard nodejs project
type('node ..\my-node-app\\app.js' + Key.ENTER)
util.close_firewall_alert_continue()
wait("server-running.png")
run('explorer "http://localhost:3000"')
wait("localhost.png")
closeApp("Edge")
wait(5)
run("turbo stop test")
wait(10)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))