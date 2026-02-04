script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)

util.pre_test()

sample_file = os.path.join(util.desktop, "MANUAL.txt")
html_file = os.path.join(util.desktop, "manual.html")
doc_file = os.path.join(util.desktop, "manual.docx")

# Test turbo run
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
# Convert website to text file
paste('turbo run pandoc --offline --isolate=merge-user -- -s -r html https://pandoc.org/MANUAL.html -o ' + sample_file)
wait(2)
type(Key.ENTER)
assert(util.file_exists(sample_file, 60))
# Convert text file to HTML
paste('turbo run pandoc --offline --isolate=merge-user -- -s ' + sample_file + ' -o ' + html_file)
wait(2)
type(Key.ENTER)
assert(util.file_exists(html_file, 60))
# Convert text file to DOCX
paste('turbo run pandoc --offline --isolate=merge-user -- -s ' + sample_file + ' -o ' + doc_file)
wait(2)
type(Key.ENTER)
assert(util.file_exists(doc_file, 60))
closeApp("Command Prompt")

# Open the converted documents
run("explorer " + sample_file)
wait("txt-sample.png")
closeApp("Notepad")
run("explorer " + os.path.join(util.desktop, "manual.html"))
wait("html-sample.png")
closeApp("Edge")
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
paste('turbo run tdf/libreoffice -d --enable=disablefontpreload -- ' + doc_file)
type(Key.ENTER)
wait(40) # libreoffice crashes on first launch
paste('turbo run tdf/libreoffice -d --enable=disablefontpreload -- ' + doc_file)
type(Key.ENTER)
wait("manual-docx.png",180)
App().focus("manual.docx")
wait("docx-sample.png",30)
wait(10)
if exists("welcome.png",30):
    click("welcome.png")
    wait(2)
    type(Key.F4, Key.ALT)
if exists("did-u-know.png",15):
    click("did-u-know.png")
    wait(5)
    type(Key.ENTER)
    wait(3)
click("docx-sample.png")
type(Key.F4, Key.ALT)
wait(5)


# Check if the session terminates.
util.check_running()
