script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

output_path = os.path.join(util.desktop, "drop.mp4")

# Basic operations.
wait("cmd_window.png")
type("ffmpeg --help" + Key.ENTER)
wait("ffmpeg_help.png")

type("ffmpeg -i " + os.path.join(script_path, os.pardir, "resources", "drop.avi") + " " + output_path + Key.ENTER)
assert(util.file_exists(output_path, 5))

run("turbo stop test")
wait(5)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))