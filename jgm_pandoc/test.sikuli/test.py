script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)

util.pre_test()

sample_file = os.path.join(script_path, os.pardir, "resources", "MANUAL.txt")

# Test turbo run
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
# Convert website to text file
type('turbo run pandoc --offline --isolate=merge-user -- -s -r html https://turbo.net -o "%userprofile%\\desktop\\turbonet.txt"')
type(Key.ENTER)
wait(10)
# Convert text file to HTML
type('turbo run pandoc --offline --isolate=merge-user -- -s ' + sample_file + ' -o "%userprofile%\\desktop\\manual.html"')
type(Key.ENTER)
wait(10)
# Convert text file to DOCX
type('turbo run pandoc --offline --isolate=merge-user -- -s ' + sample_file + ' -o "%userprofile%\\desktop\\manual.docx"')
type(Key.ENTER)
wait(10)
closeApp("Command Prompt")

# Open the converted documents
run("explorer " + os.path.join(util.desktop, "turbonet.txt"))
wait("turbonet-text.png")
closeApp("Notepad")
run("explorer " + os.path.join(util.desktop, "manual.html"))
wait("html-sample.png")
closeApp("Edge")
run("explorer " + os.path.join(util.desktop, "manual.docx"))
wait("docx-sample.png")
closeApp("WordPad")

# Check if the session terminates.
util.check_running()