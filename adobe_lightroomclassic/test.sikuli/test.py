script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)

util.pre_test()

def dismiss_whats_new():
    # The What's New panel is HTML, and the test launches Lightroom with
    # --enable=disablefontpreload, so the container's Adobe Clean is not always
    # registered with the system: the heading then falls back to a wider system
    # font (158 px vs 138 px at the same cap height).  The "What's New" text crop
    # scores ~0.45 on the real dialog in that state - below SikuliX' 0.7, and
    # below the ~0.51 it reaches on unrelated screens - so it cannot gate this
    # step (run 34925411368).  The close button is drawn rather than typed, and
    # scores 0.98 with the dialog up vs <= 0.40 without it either way.
    wait("whats_new_close.png", 120)
    wait(30)  # the panel keeps loading its content after it first paints
    click("whats_new_close.png")
    if exists("whats_new_close.png", 5):
        type(Key.ESC)  # fall back to the previous dismissal
    assert waitVanish("whats_new_close.png", 20), "What's New dialog did not close"


# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test of `turbo run`.
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
paste('turbo run lightroomclassic --using=creativeclouddesktop,isolate-edge-wc --offline --enable=disablefontpreload --name=test' + util.read_extra())
type(Key.ENTER)

# Minimize the command prompt
App().focus("Command Prompt")
type(Key.DOWN, Key.WIN)

dismiss_whats_new()
wait("getting_started.png",20)
wait(3)
type(Key.ESC)
wait("lightroomcc_window.png",30)
type("q", Key.CTRL)
click(Pattern("quit.png").targetOffset(101,28))
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Adobe Lightroom Classic.lnk"))
dismiss_whats_new()
wait("getting_started.png",20)
wait(3)
type(Key.ESC)

# Basic operations.
wait("lightroomcc_window.png",30)
wait(5)
type("i", Key.CTRL + Key.SHIFT)
wait("culling-tip.png",30)
wait(5)
type(Key.ESC)
click("import_select_source.png")
click("import_select_source_menu.png")
wait("import_location.png",20)
paste(os.path.join(script_path, os.pardir, "resources"))
type(Key.ENTER)
wait(2)
type(Key.ENTER)
wait("import_thumbnail.png",10)
click("import_import.png")
wait("import_done.png",20)
type("d")
wait(2) # Wait for Edit panel to load.
click(Pattern("develop_mode.png").targetOffset(181,-96),15)
type("r")
wait(2)
type("x")
wait(2)
type(Key.ENTER)
wait("adjusted.png",15)
type("e", Key.CTRL + Key.SHIFT)
wait("export.png",15)
type(Key.ENTER)

# Check "help".
type(Key.F1)
wait("help_url.png",30)
if App("Edge").isRunning(10):
    util.close_app("Edge")
wait(10)
if exists("import_select_source.png",10):
    wait(2)
    click("import_cancel.png")
type("q", Key.CTRL)
click(Pattern("quit.png").targetOffset(101,28))
wait(30)

# Check if the session terminates.
util.check_running()

# Export might be slow.
assert(util.file_exists(os.path.join(util.desktop, "Untitled Export", "Nikon-D3500-Shotkit.jpg"), 5))