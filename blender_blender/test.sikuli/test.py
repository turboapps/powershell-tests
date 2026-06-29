script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
resources = os.path.join(script_path, os.pardir, "resources")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test()

# Test of `turbo run`.
wait("blender-continue.png,60")
wait(3)
run("turbo stop test")

# Launch the app.
blenderfile = os.path.join(script_path, os.pardir, "resources", "cupcakes.blend")
run("explorer " + blenderfile)

# Basic operations.
wait("blender-continue.png,60")
wait(3)
click("blender-continue.png")
wait(3)
type(Key.ESC)
wait("cupcakes-loaded.png")
click("cupcakes-loaded.png")
type(Key.NUM1)
click(Pattern("render.png").targetOffset(-12,0))
wait("cupcake-rendered.png,60")
closeApp("Blender")

# Check if the session terminates.
util.check_running()