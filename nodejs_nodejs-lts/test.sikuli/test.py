# The tests for nodejs/nodejs and nodejs/nodejs-lts are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test(no_min=True)

# Minimize the sikulix console
if exists("sikulix-console.png",15):
    click("sikulix-console.png")
    wait(2)
    type(Key.DOWN, Key.WIN)

# Test cpp nodejs project.
type('cd my-node-cpp-app' + Key.ENTER)
wait(3)
type('npm install node-addon-api@8' + Key.ENTER)
wait(30)
type('npx --yes node-gyp configure' + Key.ENTER)
wait(40)
type('npx --yes node-gyp build' + Key.ENTER)
wait(40)
type('node index.js' + Key.ENTER)
wait(20)
wait("indexjs-result.png",60)

# Test standard nodejs project.
type('node ..\my-node-app\\app.js' + Key.ENTER)
wait("server-running.png")
run('explorer "http://localhost:3000"')
wait("localhost.png")
closeApp("Edge")
wait(5)
os.system('cmd /c taskkill /f /im "vctip.exe" /t')
run("turbo stop test")
wait(10)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))
