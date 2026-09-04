script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# Opening a folder raises the workspace-trust modal, and without trust the C# Dev
# Kit refuses to run ("Unable to execute C# Dev Kit command. Some features execute
# code and can only run in a trusted workspace") - the window stays in Restricted
# Mode and the run produces no output at all, so no wait length can rescue it. The
# old check keyed on a bare checkbox glyph, which is ambiguous and did not match;
# trust_folder.png cannot be used either because it bakes in an absolute path from
# an older staging location. Key on the button, and fall back to the Restricted
# Mode banner if the modal has already been dismissed.
def grant_workspace_trust(timeout=30):
    if exists("trust_folder_yes.png", timeout):
        click("trust_folder_yes.png")
        wait(3)
        return True
    # No modal: the folder opened straight into Restricted Mode, either because
    # VS Code remembers a previous decline or because it never prompted.
    # restricted_mode_banner.png is the *file* wording ("Trust this window") and
    # cannot match the folder banner ("Trust this folder"), so key on the Manage
    # link, which is common to both, and grant trust in the editor it opens.
    if exists("restricted_mode_manage.png", 10):
        click("restricted_mode_manage.png")
        if exists("workspace_trust_window.png", 20):
            click("workspace_trust_button.png")
            wait(5)
            if exists("workspace_trust_window.png", 3):
                type("w", Key.CTRL)   # close the Workspace Trust tab
                wait(2)
    # Trust is granted once the Restricted Mode banner is gone.
    return not exists("restricted_mode_manage.png", 5)

# The file-trust prompt only appears while the folder is still untrusted; once
# trust has been granted VS Code remembers it, so it must be optional.
def dismiss_file_trust():
    if exists("remember-checkbox.png",5):
        click("remember-checkbox.png")
        type(Key.TAB)
        type(Key.SPACE)
        if exists("trust-continue.png",20):
            click("trust-continue.png")

# Ctrl+O opens the file dialog, but the pasted path is intermittently swallowed:
# the autocomplete list takes the Enter and navigates into the folder instead of
# opening the file, leaving the dialog up with an empty File name box, and the
# tab wait that follows then fails. Confirm the tab actually opened and retry
# once. Paths are normalised because the dialog resolves ".." oddly.
def open_file(path, tab_image, timeout=60):
    path = os.path.normpath(path)
    for attempt in range(2):
        if not exists("open_location.png", 2):
            type("o", Key.CTRL)
            wait("open_location.png")
        wait(2)
        paste(path)
        wait(2)
        type(Key.ENTER)
        dismiss_file_trust()
        if exists(tab_image, timeout):
            return True
    return False

# Test of `turbo run`.
if exists("vscode-signin.png",60):
    type(Key.ESC)
wait("code_window_2.png",20)
run("turbo stop test")

# Install the extensions
extensions = "code --install-extension ms-python.python --install-extension ms-vscode.cpptools --install-extension ms-vscode.cpptools-extension-pack --install-extension vscjava.vscode-java-pack --install-extension ms-dotnettools.csdevkit --install-extension dbaeumer.vscode-eslint --install-extension golang.go --install-extension shopify.ruby-extensions-pack --force"
turbocmd = "turbo run vscode-x64 --isolate=merge-user --using=python/python-x64,eclipse/temurin-lts,microsoft/dotnet-sdk-x64:8 --startup-file=cmd -- /C "
run(turbocmd + extensions)
            
# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Visual Studio Code", "Visual Studio Code.lnk"))
if exists("vscode-signin.png",60):
    type(Key.ESC)
wait("code_window_2.png",20)
click("code_window_2.png")
# Activate and maximize the app window.
app_window = App().focus("Visual Studio Code")
if app_window.isValid():
    type(Key.UP, Key.WIN)

# Extension for Python and shell extension.
python_save_path = os.path.join(util.desktop, "hello_world.py")
type("n", Key.CTRL)
paste('print("Hello World!")')
wait(2)
type("s", Key.CTRL)
wait("save_location.png")
paste(python_save_path)
wait(2)
type(Key.ENTER)
assert(util.file_exists(python_save_path, 5))
click("tab_python.png")
type(Key.F4, Key.ALT)
wait(10)
run("explorer " + python_save_path)
wait("tab_python.png")
wait("restricted_mode_banner.png")
wait(2)
click(Pattern("restricted_mode_banner.png").targetOffset(219,2))
wait("restricted_mode_window.png")
type(Key.ENTER, Key.CTRL)
wait("restricted_mode_button.png")
click("tab_python.png")
wait("code_python.png")
click(Pattern("run_1.png").similar(0.60).targetOffset(-28,0))
wait("result_python.png")
type("w", Key.CTRL) # Python window.
wait(2)
type("w", Key.CTRL) # Restricted Mode window.
wait(2)
wait("code_window_2.png")

# Extension for C/C++.
if not open_file(os.path.join(script_path, os.pardir, "resources", "hello_world.c"),
                 "tab_c.png", 60):
    raise FindFailed("hello_world.c never opened")
click("tab_c.png")
wait("code_c.png")
type("w", Key.CTRL) # C window.
wait(2)
wait("code_window_2.png")

# Extension for Java.
if not open_file(os.path.join(script_path, os.pardir, "resources", "hello_world.java"),
                 "tab_java.png", 240):
    raise FindFailed("hello_world.java never opened")
click("tab_java.png")
wait("code_java.png")
# The Run affordance appears before the Java extension pack has finished
# activating ("Java: Activating..." / "Run: Importing projects"), and a run
# started then produces no output at all. Give the first run a window, then
# click Run again before failing.
java_run = Pattern("run_1.png").similar(0.60).targetOffset(-28,0)
wait(java_run,240)
click(java_run)
if not exists("result.png",120):
    click(java_run)
wait("result.png",240)
type("w", Key.CTRL) # Jave window.
wait(2)
wait("code_window_2.png")

# Extension for C#.
type("k", Key.CTRL)
type("o", Key.CTRL)
wait("open_folder.png")
paste(os.path.join(script_path, os.pardir, "resources", "Hello World"))
wait(2)
type(Key.ENTER)
wait("open_folder_select_folder.png")
type(Key.ENTER)
if not grant_workspace_trust(30):
    raise FindFailed("workspace trust was never granted - the C# run cannot "
                     "produce output in Restricted Mode")
# The C# Dev Kit opens its release-announcement markdown preview as the active
# tab the first time it activates, and it sits in front of the code. Its title
# carries the release name, so it cannot be matched reliably - close every
# editor instead, and let the test open the tab it wants next.
type("k", Key.CTRL)
type("w")
wait(3)
doubleClick(Pattern("solution_c_sharp.png").targetOffset(-20,17))
click("tab_c_sharp.png")
click(Pattern("run_1.png").similar(0.60).targetOffset(-28,0))
if exists("rebuild-yes.png",240):
    click("rebuild-yes.png")
# The C# run needs a first dotnet restore and build; 20 s is the odd one out
# here, every other language run in this test allows 240 s.
wait(Pattern("result.png").similar(0.80),240)
wait(10)
type("k", Key.CTRL)
type("f")
wait("code_window_2.png")
# Extension for JavaScript/TypeScript.
if not open_file(os.path.join(script_path, os.pardir, "resources", "hello_world.ts"),
                 "tab_typescript.png", 60):
    raise FindFailed("hello_world.ts never opened")
click("tab_typescript.png")
wait("code_typescript.png")
type("w", Key.CTRL) # TypeScript window.
wait("code_window_2.png")

# Extension for Go.
if not open_file(os.path.join(script_path, os.pardir, "resources", "hello_world.go"),
                 "tab_go.png", 60):
    raise FindFailed("hello_world.go never opened")
if exists("no_go.png",15):
    click(Pattern("no_go.png").targetOffset(205,-10))
click("tab_go.png")
wait("code_go.png")
type("w", Key.CTRL) # Go window.
wait(2)
type("w", Key.CTRL) # Go for VS Code window.
wait("code_window_2.png")

# Extension for Ruby.
if not open_file(os.path.join(script_path, os.pardir, "resources", "hello_world.rb"),
                 "tab_ruby.png", 60):
    raise FindFailed("hello_world.rb never opened")
click("tab_ruby.png")
wait("code_ruby.png")
type("w", Key.CTRL) # Ruby window.
wait("code_window_2.png")

# Check "help".
click("menu_help.png")
click("menu_help_doc.png")
wait("help_url.png")
wait(5)
if App("Edge").isRunning(10):
    util.close_app("Edge")
type(Key.F4, Key.ALT)
wait(20)
# Check if the session terminates.
util.check_running()
