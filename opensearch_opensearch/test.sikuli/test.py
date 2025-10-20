# The tests for opensearch/opensearch and opensearch/opensearch-config-turboserver are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test(no_min=True)

# Minimize the sikulix console
if exists("sikulix-console.png",15):
    click("sikulix-console.png")
    wait(2)
    type(Key.DOWN, Key.WIN)

# Warmup.
wait(30)
wait("opensearch_ready.png", 60)

# Test.
text = run('curl -X GET "localhost:9200/_cat/indices?v"')

# Direct string comparison doesn't work.
assert("green" in text)
assert("yellow" not in text)
assert("red" not in text)
assert("open" in text)
assert(".plugins-ml-config" in text)

PUT_EXPECTED = "{\"acknowledged\":true}"
text = run(os.path.join(script_path, os.pardir, "resources", "put.bat")) # Cannot get the character escape work.
assert(PUT_EXPECTED in text)

run("turbo stop test")
wait(10)

# Check if the session terminates.
assert("test" not in run("turbo sessions"))
