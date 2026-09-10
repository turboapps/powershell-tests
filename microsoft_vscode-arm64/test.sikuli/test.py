script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# turbo try -d launches VS Code detached and Windows does not always grant it the
# foreground. When it does not, the taskbar shows the VS Code button flashing for
# attention while the keyboard focus ring sits on the Start button, and a
# keystroke never reaches the app: on the runs that fail at the wait below, the
# frames either side of the old type(Key.ESC) differ by 0 px and the modal is
# still up. vscode-signin.png is the modal's own "Continue without Signing In"
# button, so click it rather than trusting a keystroke, and click again if the
# first click only served to activate the window.
def dismiss_signin():
    click("vscode-signin.png")
    if exists("vscode-signin.png", 5):
        click("vscode-signin.png")

# Test of `turbo run`.
if exists("vscode-signin.png",60):
    dismiss_signin()
wait("code_window_2.png",20)
run("turbo stop test")

# Install the extensions
extensions = "code --install-extension ms-python.python --install-extension ms-vscode.cpptools --install-extension ms-vscode.cpptools-extension-pack --install-extension vscjava.vscode-java-pack --install-extension ms-dotnettools.csdevkit --install-extension dbaeumer.vscode-eslint --install-extension golang.go --install-extension shopify.ruby-extensions-pack --force"
turbocmd = "turbo run vscode-arm64 --isolate=merge-user --using=python/python-arm64,eclipse/temurin-lts-arm64,microsoft/dotnet-sdk-arm64 --startup-file=cmd -- /C "
run(turbocmd + extensions)
            
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
type("o", Key.CTRL)
wait("open_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "hello_world.c"))
wait(2)
type(Key.ENTER)
wait("remember-checkbox.png")
click("remember-checkbox.png")
type(Key.TAB)
type(Key.SPACE)
if exists("trust-continue.png",20):
    click("trust-continue.png")
click("tab_c.png")
wait("code_c.png")
type("w", Key.CTRL) # C window.
wait(2)
wait("code_window_2.png")

# Extension for Java.
type("o", Key.CTRL)
wait("open_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "hello_world.java"))
wait(2)
type(Key.ENTER)
wait("tab_java.png",240)
click("tab_java.png")
wait("code_java.png")
wait(Pattern("run_1.png").similar(0.60).targetOffset(-28,0),240)
click(Pattern("run_1.png").similar(0.60).targetOffset(-28,0))
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
# The Explorer tree can take well past the ambient timeout to populate after C#
# Dev Kit loads the project.
wait(Pattern("solution_c_sharp.png"), 180)
doubleClick(Pattern("solution_c_sharp.png").targetOffset(-20,17))
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
wait("code_window_2.png")
# Extension for JavaScript/TypeScript.
type("o", Key.CTRL)
wait("open_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "hello_world.ts"))
wait(2)
type(Key.ENTER)
click("tab_typescript.png")
wait("code_typescript.png")
type("w", Key.CTRL) # TypeScript window.
wait("code_window_2.png")

# Extension for Go.
type("o", Key.CTRL)
wait("open_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "hello_world.go"))
wait(2)
type(Key.ENTER)
if exists("no_go.png",15):
    click(Pattern("no_go.png").targetOffset(205,-10))
click("tab_go.png")
wait("code_go.png")
type("w", Key.CTRL) # Go window.
wait(2)
type("w", Key.CTRL) # Go for VS Code window.
wait("code_window_2.png")

# Extension for Ruby.
type("o", Key.CTRL)
wait("open_location.png")
paste(os.path.join(script_path, os.pardir, "resources", "hello_world.rb"))
wait(2)
type(Key.ENTER)
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
