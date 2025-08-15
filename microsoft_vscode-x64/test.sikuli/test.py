script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(50)
util.pre_test()

# Test of `turbo run`.
wait("welcome-tab.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Visual Studio Code", "Visual Studio Code.lnk"))
wait("welcome-tab.png")
# Activate and maximize the app window.
app_window = App().focus("Visual Studio Code")
if app_window.isValid():
    type(Key.UP, Key.WIN)

# Extension for Python and shell extension.
python_save_path = os.path.join(util.desktop, "hello_world.py")
type("n", Key.CTRL)
type('print("Hello World!")')
type("s", Key.CTRL)
wait("save_location.png")
type(python_save_path + Key.ENTER)
assert(util.file_exists(python_save_path, 5))
wait("extension_python.png")
wait(2)
click(Pattern("extension_python.png").targetOffset(59,26))
wait("install_complete_python.png", 300)
type(Key.F4, Key.ALT)
wait(10)
run("explorer " + python_save_path)
wait("tab-walkthrough.png")
wait("restricted_mode_banner.png")
wait(2)
click(Pattern("restricted_mode_banner.png").targetOffset(219,2))
wait("restricted_mode_window.png")
type(Key.ENTER, Key.CTRL)
wait("restricted_mode_button.png")
click("tab_python.png")
wait("code_python.png")
click(Pattern("run_1.png").targetOffset(-28,0))
wait("result_python.png")
type("w", Key.CTRL) # Python window.
wait(2)
type("w", Key.CTRL) # Restricted Mode window.
wait(2)
type("w", Key.CTRL) # Python Extension window.
wait("code_window_2.png")

# Extension for C/C++.
type("o", Key.CTRL)
wait("open_location.png")
type(os.path.join(script_path, os.pardir, "resources", "hello_world.c") + Key.ENTER)
wait("trust_file.png")
wait(2)
click(Pattern("trust_file.png").targetOffset(-157,65))
click(Pattern("trust_file.png").targetOffset(-34,109))
wait("extension_c.png")
wait(2)
click(Pattern("extension_c.png").targetOffset(28,31))
wait(Pattern("install_complete_1.png").similar(0.85), 240)
if exists("extensions_pre-release_c.png",15):
    click(Pattern("extensions_pre-release_c.png").targetOffset(197,27))
click("tab_c.png")
wait("code_c.png")
type("w", Key.CTRL) # C window.
wait(2)
type("w", Key.CTRL) # C Extension window.
wait("code_window_2.png")

# Extension for Java.
type("o", Key.CTRL)
wait("open_location.png")
type(os.path.join(script_path, os.pardir, "resources", "hello_world.java") + Key.ENTER)
wait("extension_java.png")
wait(2)
click(Pattern("extension_java.png").targetOffset(32,22))
wait("install_complete_2.png", 240)
wait("tab_java.png",240)
click("tab_java.png")
wait("code_java.png")
wait("java-tab.png",240)
click("java-tab.png")
wait(Pattern("run_1.png").targetOffset(-28,0))
click(Pattern("run_1.png").targetOffset(-28,0))
wait("result.png")
type("w", Key.CTRL) # Jave window.
wait(2)
type("w", Key.CTRL) # Java Extension window.
wait(2)
type("w", Key.CTRL) # JDK window
wait("code_window_2.png")

# Extension for C#.
type("k", Key.CTRL)
type("o", Key.CTRL)
wait("open_folder.png")
type(os.path.join(script_path, os.pardir, "resources", "Hello World") + Key.ENTER)
wait("open_folder_select_folder.png")
type(Key.ENTER)
wait("trust_folder.png")
wait(2)
click(Pattern("trust_folder.png").targetOffset(-159,95))
click(Pattern("trust_folder.png").targetOffset(-69,138))
doubleClick(Pattern("solution_c_sharp.png").targetOffset(-20,17))
wait("extension_c_sharp.png")
wait(2)
click(Pattern("extension_c_sharp.png").targetOffset(27,23))
wait(Pattern("install_complete_2.png").similar(0.95), 240)
click("tab_c_sharp.png")
wait("code_c_sharp.png")
if exists("get-started-csharp.png",15):
    click("tab_c_sharp.png")
wait("projects-helloworld.png",240)
click(Pattern("run_1.png").targetOffset(-28,0))
wait(Pattern("result.png").similar(0.80), 240)
type("k", Key.CTRL)
type("f")
wait("welcome-tab.png")

# Extension for JavaScript/TypeScript.
type("o", Key.CTRL)
wait("open_location.png")
type(os.path.join(script_path, os.pardir, "resources", "hello_world.ts") + Key.ENTER)
click("extensions_buttion.png")
click(Pattern("extensions_search_typescript.png").targetOffset(-95,14))
type("@id:dbaeumer.vscode-eslint")
click(Pattern("extension_typescript.png").targetOffset(108,11))
wait(Pattern("install_complete_1.png").similar(0.85), 240)
click("es-lint-logo.png")
click("tab_typescript.png")
wait("code_typescript.png")
type("w", Key.CTRL) # TypeScript window.
wait(2)
type("w", Key.CTRL) # TypeScript Extension window.
wait("code_window_2.png")

# Extension for Go.
type("o", Key.CTRL)
wait("open_location.png")
type(os.path.join(script_path, os.pardir, "resources", "hello_world.go") + Key.ENTER)
wait("extension_go.png")
wait(2)
click(Pattern("extension_go.png").targetOffset(24,24))
click("trust-publisher-install.png")
wait(Pattern("install_complete_1.png").similar(0.85), 240)
if exists("no_go.png",15):
    click(Pattern("no_go.png").targetOffset(205,-10))
click("tab_go.png")
wait("code_go.png")
type("w", Key.CTRL) # Go window.
wait(2)
type("w", Key.CTRL) # Go for VS Code window.
wait(2)
type("w", Key.CTRL) # Go Extension window.
wait("code_window_2.png")

# Extension for Rust.
type("o", Key.CTRL)
wait("open_location.png")
type(os.path.join(script_path, os.pardir, "resources", "hello_world.rs") + Key.ENTER)
click(Pattern("extensions_search_rust.png").targetOffset(-43,12))
type("a", Key.CTRL)
type("@id:rust-lang.rust-analyzer")
click("install-extension.png")
click("trust-publisher-install.png")
if exists(Pattern("no_rust_1.png").similar(0.90),15):
    wait(2)
    click(Pattern("no_rust_1.png").similar(0.90).targetOffset(205,-23))
if exists("no_rust_2.png",15):
    wait(2)
    click(Pattern("no_rust_2.png").targetOffset(205,-29))
wait("install_complete_rust.png")
type("w", Key.CTRL) # Rust Extension window.
click("tab_rust.png")
wait("code_rust.png")
type("w", Key.CTRL) # Rust window.
wait(2)
type("w", Key.CTRL) # Rust Extension window or Rust Welcome window.
wait("code_window_2.png")

# Extension for Ruby.
type("o", Key.CTRL)
wait("open_location.png")
type(os.path.join(script_path, os.pardir, "resources", "hello_world.rb") + Key.ENTER)
click(Pattern("extensions_search_ruby.png").targetOffset(-97,17))
type("a", Key.CTRL)
type("@id:shopify.ruby-extensions-pack")
click("install-extension.png")
click("trust-publishers.png")
wait(Pattern("install_complete_1.png").similar(0.85), 240)
if exists("theme_ruby.png",15):
    type(Key.ESC)
click("tab_ruby.png")
wait("code_ruby.png")
type("w", Key.CTRL) # Ruby window.
wait(2)
type("w", Key.CTRL) # Ruby Extension window.
wait("code_window_2.png")

# Check "help".
click("menu_help.png")
click("menu_help_doc.png")
wait("help_url.png")
closeApp("Edge")
type(Key.F4, Key.ALT)
wait(20)
# Check if the session terminates.
util.check_running()
