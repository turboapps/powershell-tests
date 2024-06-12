# The tests for videolan/vlc and videolan/vlc-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

video_path = os.path.join(script_path, os.pardir, "resources", "drop.avi")

setAutoWaitTimeout(20)
util.pre_test()

# Test of `turbo run`.
wait("vlc_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "VideoLAN", "VLC media player.lnk"))
wait("vlc_window.png")

# Basic operations and check help.
type("o", Key.CTRL)
wait("file_location.png")
type(video_path + Key.ENTER)
wait("video.png")
wait(10)
type(Key.F1)
wait("vlc_help.png")
type(Key.ESC)
type(Key.F4, Key.ALT)

# Open avi with file association.
run("explorer " + video_path)
click("default_vlc.png")
click(Pattern("default_always.png").targetOffset(-130,-2))
click("default_ok.png")
wait("video.png")
wait(10)
type(Key.F4, Key.ALT)

# Other start up items should wock.
run("explorer " + os.path.join(util.start_menu, "VideoLAN", "VLC media player - reset preferences and cache files.lnk"))
wait(15) # It should not cause error.
run("explorer " + os.path.join(util.start_menu, "VideoLAN", "VLC media player skinned.lnk"))
wait("vlc_skinned_window.png")
type("q", Key.CTRL)

# Check if the session terminates.
util.check_running()