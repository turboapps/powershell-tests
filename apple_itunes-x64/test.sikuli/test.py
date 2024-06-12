script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

audio_path = os.path.join(script_path, os.pardir, "resources", "StarWars3.wav")

setAutoWaitTimeout(50)
util.pre_test()

# Test of `turbo run`.
if exists("audio-warning.png"):
    type(Key.ENTER)
wait("itunes-welcome.png")
click(Pattern("itunes-welcome.png").targetOffset(-197,115))
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.desktop, "iTunes.lnk"))
if exists("audio-warning.png"):
    type(Key.ENTER)
wait("itunes-welcome.png")
click(Pattern("itunes-welcome.png").targetOffset(-197,115))
wait(10)

# Basic operations and check help.
click("songs.png")
type("o", Key.CTRL)
wait("file_location.png")
type(audio_path + Key.ENTER)
wait("starwars.png")
doubleClick("starwars.png")
wait(5)
type(Key.F1)
wait("user-guide.png")
type(Key.F4, Key.ALT)
wait(3)
type(Key.F4, Key.ALT)

# Set default player.
type("i", Key.WIN)
wait("windows_setting_window.png")
type("Default apps")
click("windows_setting_default.png")
click("music-player.png")
wait(2)
click("itunes-default.png")
wait(3)
type(Key.F4, Key.ALT)
run("explorer " + audio_path)
if exists("audio-warning2.png"):
    click(Pattern("audio-warning2.png").targetOffset(139,34))
wait("starwars.png")
wait(20)
wait("starwars.png")
click("starwars.png")
type(Key.F4, Key.ALT)
wait(40)


# Check if the session terminates.
util.check_running()