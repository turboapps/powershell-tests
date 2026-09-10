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

# turbo try -d launches VS Code detached and Windows does not always grant it the
# foreground. When it does not, the taskbar shows the VS Code button flashing for
# attention while the keyboard focus ring sits on the Start button, and a
# keystroke never reaches the app - the frames either side of the old
# type(Key.ESC) here differ by 0 px, and the wait that follows then fails
# (run 34097555049 line 73, run 34417314575 line 73, and every arm64 run that
# dies at line 14). vscode-signin.png is the modal's own "Continue without
# Signing In" button, so click it rather than trusting a keystroke, and click
# again if the first click only served to activate the window.
def dismiss_signin():
    click("vscode-signin.png")
    if exists("vscode-signin.png", 5):
        click("vscode-signin.png")

# The folder-trust dialog ("Do you trust the authors of the files in this
# folder?" / "Trust Folder & Continue") can surface tens of seconds after a file
# is opened - well after open_file's own 20 s window on trust-continue.png has
# closed - and it then sits on top of the window this wait is looking for. In run
# 34419163811 it appeared moments after that window expired and line 132 failed
# with the dialog plainly visible in the frame. Clear it before giving up.
def wait_code_window(timeout=60):
    if exists("code_window_2.png", 10):
        return True
    if exists("trust-continue.png", 3):
        click("trust-continue.png")
        wait(3)
    return exists("code_window_2.png", timeout)

# Alt+F4 closes the VS Code window, but the Turbo session can outlive it and a
# launch that lands in that gap dies with "Failed to start application in already
# running session" on a bare desktop: the client logs "Existing session with same
# sandbox is not running" and then switches to LaunchInSession anyway
# (turbo_20260910_001227_3296.log in run 34419196293), hangs ~36 s and gives up.
# Wait for the session and the process to actually go quiet first, and if the
# error dialog still appears, clear it and launch again.
def reopen_in_new_window(path, tab_image, attempts=3):
    for attempt in range(attempts):
        util.wait_app_quiet("Code.exe", 120)
        run("explorer " + path)
        if exists(tab_image, 90):
            return True
        if exists("turbo-session-error.png", 5):
            Debug.user("reopen_in_new_window: Turbo refused the launch, clearing "
                       "the error and retrying")
            click(Pattern("turbo-session-error.png").targetOffset(145,34))
            wait(5)
    return False

# Test of `turbo run`.
if exists("vscode-signin.png",60):
    dismiss_signin()
wait("code_window_2.png",20)
run("turbo stop test")

# Install the extensions
extensions = "code --install-extension ms-python.python --install-extension ms-vscode.cpptools --install-extension ms-vscode.cpptools-extension-pack --install-extension vscjava.vscode-java-pack --install-extension ms-dotnettools.csdevkit --install-extension dbaeumer.vscode-eslint --install-extension golang.go --install-extension shopify.ruby-extensions-pack --force"
turbocmd = "turbo run vscode-x64 --isolate=merge-user --using=python/python-x64,eclipse/temurin-lts,microsoft/dotnet-sdk-x64:8 --startup-file=cmd -- /C "
run(turbocmd + extensions)
            
# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Visual Studio Code", "Visual Studio Code.lnk"))
if exists("vscode-signin.png",60):
    dismiss_signin()
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
if not reopen_in_new_window(python_save_path, "tab_python.png"):
    raise FindFailed("hello_world.py never reopened in a new window")
wait("restricted_mode_banner.png")
wait(2)
click(Pattern("restricted_mode_banner.png").targetOffset(219,2))
wait("restricted_mode_window.png")
type(Key.ENTER, Key.CTRL)
wait("restricted_mode_button.png")
click("tab_python.png")
wait("code_python.png")
# No Run affordance here means the Python extension is not in this window rather
# than that the button is slow: VS Code is still offering "Do you want to install
# the recommended 'Python' extension" (run 34510865844, where the editor actions
# carried only split and "..."). Name that, instead of failing on a missing image.
python_run = Pattern("run_1.png").similar(0.60).targetOffset(-28,0)
if not exists(python_run, 120) and exists("python-extension-recommendation.png", 5):
    raise FindFailed("the Python extension is missing from this window - VS Code "
                     "is still recommending it, so no Run button was contributed")
click(python_run)
wait("result_python.png")
type("w", Key.CTRL) # Python window.
wait(2)
type("w", Key.CTRL) # Restricted Mode window.
wait(2)
if not wait_code_window():
    raise FindFailed("code_window_2.png never appeared")

# Extension for C/C++.
if not open_file(os.path.join(script_path, os.pardir, "resources", "hello_world.c"),
                 "tab_c.png", 60):
    raise FindFailed("hello_world.c never opened")
click("tab_c.png")
wait("code_c.png")
type("w", Key.CTRL) # C window.
wait(2)
if not wait_code_window():
    raise FindFailed("code_window_2.png never appeared")

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
if not wait_code_window():
    raise FindFailed("code_window_2.png never appeared")

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
# The Explorer tree can take well past the ambient 50 s to populate after C# Dev
# Kit loads the project: runs 34510877179 and 34510888131 both failed here with
# the pane reading "HELLO WORLD" and not a single row under it.
wait(Pattern("solution_c_sharp.png"), 180)
doubleClick(Pattern("solution_c_sharp.png").targetOffset(-20,17))
click("tab_c_sharp.png")
wait(3)
# The editor Run button is unreliable here: the click lands on it - the hover
# highlight paints, and that 30x21 box is the only thing on the whole screen that
# changes - but VS Code never acts on it and no run starts, even given 900 s.
# The keyboard still works, so fall back to Ctrl+F5. Because this workspace
# carries no launch.json, that walks two quick picks in turn.
csharp_run = Pattern("run_1.png").similar(0.60).targetOffset(-28,0)
wait(csharp_run,240)
click(csharp_run)
if not exists("result.png",60):
    # Move off the button first: the click leaves the cursor on it, and that hover
    # drops run_1.png from 0.63 to 0.555 - under its own similar(0.60) - so it can
    # no longer be re-found while the mouse rests there.
    mouseMove(Location(960,400))
    wait(2)
    type(Key.F5, Key.CTRL)
    # "Select debugger" opens with NO active row, so a bare Enter is a no-op (two
    # of them left it untouched for 300 s). DOWN activates the suggested C# entry.
    if exists(Pattern("select-debugger.png").similar(0.70),60):
        type(Key.DOWN)
        wait(2)
        type(Key.ENTER)
    # "Select Launch Configuration" follows, and this one opens with its first row
    # already active, so DOWN moves on to "C#: Hello World" - the entry observed
    # to actually print. Keyed on its own reference: the debugger one cannot tell
    # these two apart reliably, both being "Select ..." in the same box.
    if exists(Pattern("select-launch-config.png").similar(0.70),60):
        type(Key.DOWN)
        wait(2)
        type(Key.ENTER)
# The C# run needs a first dotnet restore and build; 20 s is the odd one out
# here, every other language run in this test allows 240 s.
wait(Pattern("result.png").similar(0.80),240)
wait(10)
type("k", Key.CTRL)
type("f")
if not wait_code_window():
    raise FindFailed("code_window_2.png never appeared")
# Extension for JavaScript/TypeScript.
if not open_file(os.path.join(script_path, os.pardir, "resources", "hello_world.ts"),
                 "tab_typescript.png", 60):
    raise FindFailed("hello_world.ts never opened")
click("tab_typescript.png")
wait("code_typescript.png")
type("w", Key.CTRL) # TypeScript window.
if not wait_code_window():
    raise FindFailed("code_window_2.png never appeared")

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
if not wait_code_window():
    raise FindFailed("code_window_2.png never appeared")

# Extension for Ruby.
if not open_file(os.path.join(script_path, os.pardir, "resources", "hello_world.rb"),
                 "tab_ruby.png", 60):
    raise FindFailed("hello_world.rb never opened")
click("tab_ruby.png")
wait("code_ruby.png")
type("w", Key.CTRL) # Ruby window.
if not wait_code_window():
    raise FindFailed("code_window_2.png never appeared")

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
