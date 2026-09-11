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
wait("vlc_window.png",60)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "VideoLAN", "VLC media player.lnk"))
wait("vlc_window.png",60)

# Basic operations and check help.
#
# VLC does not reliably own the foreground once its window paints, so Ctrl+O is
# swallowed and the Open Media dialog never appears. In App Tests run
# 34423192441 the step frames catch it exactly: at 003-type.jpg - the frame
# taken immediately before the hotkey - the title bar text is grey and the
# taskbar button carries the short inactive dash, where the same frame in the
# passing run has black title text and the blue active bar; Ctrl+O then changes
# not one pixel on screen (003 and 004 are identical), and by the FAILED frame
# 20 s later the taskbar button has gone red, which is how Windows renders a
# SetForegroundWindow that was denied. The title still reads plain "VLC media
# player" throughout, so the app is alive and pumping messages - it just never
# had the keyboard.
#
# The launch chain is the reason: run("explorer ...lnk") hands off through
# turboplay to turbo to vlc.exe, and when those foreground rights do not carry
# all the way VLC comes up behind. App().focus() cannot rescue it either, since
# the hidden SikuliX process holds no foreground rights of its own - which is
# why the same signature has failed on xvm 26.9.20, 26.9.26 and 26.9.29 and
# passed on all three, and why the two sibling vlc tests passed in the very run
# the third failed. Padding a wait() in front of the hotkey cannot fix it, so
# check the outcome and press again, the way klayout does for its own swallowed
# Ctrl+Shift+O. The dialog check only gates the retry - file_location.png below
# is still the assertion, so this cannot fail a run on its own.
util.activate_app_window("VLC media player", 10)
type("o", Key.CTRL)
if not exists("file_location.png", 10):
    util.activate_app_window("VLC media player", 10)
    type("o", Key.CTRL)
wait("file_location.png")
util.open_file_in_dialog("file_location.png", video_path)
wait("video.png")
wait(10)
type(Key.F1)
wait("vlc_help.png")
type(Key.ESC)
type(Key.F4, Key.ALT)

# Open avi with file association.
rightClick("drop-desktop-icon.png")
click("open-with.png")
click("open-with-vlc.png")
wait("video.png")
wait(10)
type(Key.F4, Key.ALT)

# Other start up items should wock.
run("explorer " + os.path.join(util.start_menu, "VideoLAN", "VLC media player - reset preferences and cache files.lnk"))
wait(15) # It should not cause error.
run("explorer " + os.path.join(util.start_menu, "VideoLAN", "VLC media player skinned.lnk"))
wait("vlc_skinned_window.png")
type("q", Key.CTRL)
wait(20)

# Check if the session terminates.
util.check_running()