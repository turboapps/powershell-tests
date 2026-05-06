script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

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
if exists("extensions_pre-release_c.png",20):
    click(Pattern("extensions_pre-release_c.png").targetOffset(197,27))
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
wait("result.png")
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
doubleClick(Pattern("solution_c_sharp.png").targetOffset(-20,17))
click("tab_c_sharp.png")
click(Pattern("run_1.png").similar(0.60).targetOffset(-28,0))
if exists("rebuild-yes.png",240):
    click("rebuild-yes.png")
wait(Pattern("result.png").similar(0.80),20)
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
closeApp("Edge")
type(Key.F4, Key.ALT)
wait(20)
# Check if the session terminates.
util.check_running()
