script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(60)
util.pre_test(no_min=True)

# Minimize the sikulix console
if exists("sikulix-console.png",20):
    App().focus("java.exe")
    type(Key.DOWN, Key.WIN)

output_path = os.path.join(util.desktop, "cat-mummies.mp4")

# Basic operations.
wait("cmd_window.png")
type("C:\\yt-dlp\\yt-dlp.exe --help" + Key.ENTER)
wait("yt-dlp_help.png",90)
run("turbo stop test")
wait(2)

# YouTube might block IP. Use BBC instead.
run("turbo run yt-dlp https:////www.bbc.com//reel//video//p0jr4z6k//why-tonnes-of-mummified-cats-ended-up-in-england --isolate=merge-user -- -o " + output_path)
assert(util.file_exists(output_path, 5))
wait(5)

# Check if the session terminates.
util.check_running()