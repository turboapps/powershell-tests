script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

output = os.path.join(util.desktop, "out.txt")

# Check the parsing results.
assert(util.file_exists(output, 60))
with open(output, 'r') as file:
    content = file.read()
    assert("our score and seven years ago" in content)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))