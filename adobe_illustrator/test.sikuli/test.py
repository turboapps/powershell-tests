script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(90)

util.pre_test()

save_location = os.path.join(util.desktop, "Untitled-1.ai")

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Login to Adobe Creative Cloud Desktop
util.launch_adobe_cc(username, password)

# Test of `turbo run`.
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(10)
paste('turbo run illustrator --using=creativeclouddesktop,vcredist --offline --enable=disablefontpreload --name=test')
wait(3)
type(Key.ENTER)
if exists("whats_new.png"):
    type(Key.ESC)
wait("ai_window.png")
run("turbo stop test")
wait(10)

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.start_menu, "Adobe Illustrator"))
if exists("whats_new.png"):
    type(Key.ESC)

# Basic operations.
wait("ai_window.png")
wait(10)
type("n", Key.CTRL + Key.SHIFT)
wait(10)
click("open_location.png")
paste("C:\\Program Files\\Adobe\\Adobe Illustrator 2026\\Cool Extras\\en_US\\Templates\\Blank Templates\\Tshirt.ait")
type(Key.ENTER)
wait("tshirt.png")
wait(3)
type("s", Key.CTRL)
wait("save_location.png")
paste(save_location)
type(Key.ENTER)
click(Pattern("save_options.png").targetOffset(-49,-1))
assert(util.file_exists(save_location, 5))
type("w", Key.CTRL)
wait(10)
run("explorer " + save_location)
wait("tshirt.png")
type(Key.F1)
wait("help.png")
type(Key.ESC)
wait(3)
type("q",Key.CTRL)
wait(10)

# Check if the session terminates.
util.check_running()
