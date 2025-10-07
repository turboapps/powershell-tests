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
if exists("sikulix-console.png"):
    App().focus("java.exe")
    type(Key.DOWN, Key.WIN)

# Test cpp nodejs project.
paste('cd my-node-cpp-app')
type(Key.ENTER)
wait(3)
paste('npm install -g node-gyp')
type(Key.ENTER)
wait(20)
paste('npm init -y')
type(Key.ENTER)
wait(20)
paste('node-gyp configure')
type(Key.ENTER)
wait(45)
paste('node-gyp build')
type(Key.ENTER)
wait(20)
paste('node index.js')
type(Key.ENTER)
wait(10)
wait("indexjs-result.png",60)

# Test standard nodejs project.
paste('node ..\my-node-app\\app.js')
type(Key.ENTER)
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
