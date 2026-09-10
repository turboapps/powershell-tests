script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# Opening a folder raises the workspace-trust modal, and without trust the C# Dev
# Kit refuses to run - the window stays in Restricted Mode and the run produces
# no output at all, so no wait length can rescue it. x64 has carried this for a
# while; arm64 only ever handled the *file*-trust prompt (remember-checkbox),
# which is a different dialog, and never granted folder trust at all.
def grant_workspace_trust(timeout=30):
    if exists("trust_folder_yes.png", timeout):
        click("trust_folder_yes.png")
        wait(3)
        return True
    # No modal: the folder opened straight into Restricted Mode, either because
    # VS Code remembers a previous decline or because it never prompted. Key on
    # the Manage link, which is common to both banner wordings, and grant trust
    # in the editor it opens.
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
# trust has been granted VS Code remembers it, so it must be optional. The old
# inline copy in the C section used a bare wait(), which raises outright when the
# dialog does not appear at all.
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

# The folder-trust dialog ("Trust Folder & Continue") can surface tens of seconds
# after a file is opened - well after open_file's own 20 s window on
# trust-continue.png has closed - and it then sits on top of the window this wait
# is looking for. Clear it before giving up.
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
# sandbox is not running" and then switches to LaunchInSession anyway, hangs
# ~36 s and gives up. Wait for the session and the process to go quiet first, and
# if the error dialog still appears, clear it and launch again.
def reopen_in_new_window(path, tab_image, attempts=3):
    for attempt in range(attempts):
        util.wait_app_quiet("Code.exe", 120)
        run("explorer " + path)
        # Wait for whichever lands first: the client blocks ~36 s before giving
        # up and a healthy launch beats that easily, so polling for both avoids
        # paying either timeout in the common case.
        for poll in range(60):
            if exists(tab_image, 2):
                return True
            if exists("turbo-session-error.png", 1):
                Debug.user("reopen_in_new_window: Turbo refused the launch into "
                           "a session it had already logged as not running; "
                           "clearing the error and retrying")
                click(Pattern("turbo-session-error.png").targetOffset(145,34))
                wait(5)
                break
    return False

def dismiss_signin():
    # ESC cancels the whole welcome wizard and leaves the window in the state the
    # rest of the test expects.
    #
    # Do NOT click vscode-signin.png to dismiss this. That image is the modal's
    # "Continue without Signing In" button, and clicking it ADVANCES the wizard
    # to its "Make It Yours" theme page rather than closing it - code_window_2
    # then never matches, which took out runs 34516501432, 34516513523 and
    # 34516524525 3/3.
    #
    # ESC only lands if the window actually holds the foreground, and turbo try
    # -d does not always get it: when it does not, the taskbar shows the VS Code
    # button flashing for attention while the keyboard focus ring sits on the
    # Start button, and the frames either side of the keystroke differ by 0 px.
    # Ask for the foreground first, and try again if the modal is still up.
    for attempt in range(3):
        util.activate_app_window("Visual Studio Code", 3)
        type(Key.ESC)
        if not exists("vscode-signin.png", 5):
            return True
        Debug.user("dismiss_signin: the sign-in modal survived ESC (attempt %d)"
                   % (attempt + 1))
    return False

# Test of `turbo run`.
if exists("vscode-signin.png",60):
    dismiss_signin()
wait("code_window_2.png",20)
run("turbo stop test")

# Install the extensions
extensions = "code --install-extension ms-python.python --install-extension ms-vscode.cpptools --install-extension ms-vscode.cpptools-extension-pack --install-extension vscjava.vscode-java-pack --install-extension ms-dotnettools.csdevkit --install-extension dbaeumer.vscode-eslint --install-extension golang.go --install-extension shopify.ruby-extensions-pack --force"
turbocmd = "turbo run vscode-arm64 --isolate=merge-user --using=python/python-arm64,eclipse/temurin-lts-arm64,microsoft/dotnet-sdk-arm64 --startup-file=cmd -- /C "
# The install runs in a container whose cmd.exe crashes often enough to cost a
# run: on x64 Turbo logged "Application exited: -1073741819" (0xC0000005) 17 s
# in, and the dump was an NX execute fault at an address inside no loaded module.
# Nothing checked that return value, so the run carried on with no extensions and
# died 40 lines later on a missing Run button. merge-user puts container writes
# in the real profile - the test already leans on that for hello_world.py - so
# the extension folders can be checked from here.
extensions_dir = os.path.join(os.environ["USERPROFILE"], ".vscode", "extensions")

def install_extensions(attempts=2):
    for attempt in range(attempts):
        run(turbocmd + extensions)
        if util.find_file(extensions_dir, "ms-python.python"):
            return True
        Debug.user("install_extensions: ms-python.python is not in %s after "
                   "attempt %d - the install container most likely crashed; "
                   "retrying" % (extensions_dir, attempt + 1))
    return False

if not install_extensions():
    raise FindFailed("the VS Code extensions never installed: the install "
                     "container exits with 0xC0000005, an NX execute fault in "
                     "cmd.exe at an address in no loaded module")
            
# Launch the app.
util.launch_shortcut(["Visual Studio Code", "Visual Studio Code.lnk"], "Microsoft VSCode ARM64.lnk")
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
# the recommended 'Python' extension". Name that, instead of failing on a missing
# image.
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
# started then produces no output at all. Give the first run a window, then click
# Run again before failing.
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
if exists("remember-checkbox.png",10):
    click("remember-checkbox.png")
    type(Key.TAB)
    type(Key.SPACE)
# The C# Dev Kit opens its release-announcement markdown preview as the active
# tab the first time it activates, and it sits in front of the code - runs
# 34509070551, 34509081355 and 34509092247 all failed in this section with
# "Preview WBD-hybrid announcement.md" covering the editor. Its title carries the
# release name, so it cannot be matched reliably; close every editor instead and
# let the test open the tab it wants next. x64 has carried this guard for a
# while, arm64 never got it.
type("k", Key.CTRL)
type("w")
wait(3)
# The Explorer tree does not always populate. The pane shows the folder root
# expanded with not a single row under it, and no wait rescues it: in run
# 34520054848 solution_c_sharp.png still scored 0.34 in the final screenshot,
# taken after a 180 s wait had already expired. The tree is only a means of
# opening Program.cs, so do not depend on it - fall back to opening the file by
# path, the way every other language in this test opens its own.
if exists(Pattern("solution_c_sharp.png"), 180):
    doubleClick(Pattern("solution_c_sharp.png").targetOffset(-20,17))
else:
    Debug.user("the Explorer tree never populated; opening Program.cs by path")
    if not open_file(os.path.join(script_path, os.pardir, "resources",
                                  "Hello World", "Program.cs"),
                     "tab_c_sharp.png", 60):
        raise FindFailed("Program.cs never opened: the Explorer tree never "
                         "populated and opening it by path failed too")
click("tab_c_sharp.png")
wait(3)
# The editor Run button is unreliable here: on x64 the click lands on it - the
# hover highlight paints, and that 30x21 box is the only thing on the whole
# screen that changes - but VS Code never acts on it and no run starts, even
# given 900 s. The keyboard still works, so fall back to Ctrl+F5. Because this
# workspace carries no launch.json, that walks two quick picks in turn. The old
# 20 s result wait here was also the odd one out; every other run in this test
# allows 240 s.
csharp_run = Pattern("run_1.png").similar(0.60).targetOffset(-28,0)
wait(csharp_run,240)
click(csharp_run)
if not exists("result.png",60):
    # Move off the button first: the click leaves the cursor on it, and that
    # hover drops run_1.png below its own similar(0.60), so it can no longer be
    # re-found while the mouse rests there.
    mouseMove(Location(960,400))
    wait(2)
    type(Key.F5, Key.CTRL)
    # "Select debugger" opens with NO active row, so a bare Enter is a no-op;
    # DOWN activates the suggested C# entry.
    if exists(Pattern("select-debugger.png").similar(0.70),60):
        type(Key.DOWN)
        wait(2)
        type(Key.ENTER)
    # "Select Launch Configuration" follows, and opens with its first row already
    # active, so DOWN moves on to "C#: Hello World".
    if exists(Pattern("select-launch-config.png").similar(0.70),60):
        type(Key.DOWN)
        wait(2)
        type(Key.ENTER)
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
