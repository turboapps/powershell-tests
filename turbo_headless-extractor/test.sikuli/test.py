script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Check the extract results.
assert(util.file_exists(os.path.join(util.desktop, "image.png"), 5))
assert(util.file_exists(os.path.join(util.desktop, "domText.txt"), 5))
assert(util.file_exists(os.path.join(util.desktop, "dom.html"), 5))
assert(util.file_exists(os.path.join(util.desktop, "links.txt"), 5))
wait(30)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))