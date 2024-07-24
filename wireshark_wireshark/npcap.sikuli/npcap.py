script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

util.pre_test()

wait("agreement.png")
click("agree.png")
click("install.png")
wait(Pattern("completed.png").similar(0.95), 90)
click("next.png")
click("finish.png")