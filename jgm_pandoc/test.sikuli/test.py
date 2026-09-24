script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
import time
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)

util.pre_test()

sample_file = os.path.join(util.desktop, "MANUAL.txt")
html_file = os.path.join(util.desktop, "manual.html")
doc_file = os.path.join(util.desktop, "manual.docx")

# Run pandoc from the console and wait for the file it writes.
#
# App Tests run 35935367711 lost the second paste outright: the step frame taken
# before the Enter shows the console focused with an empty prompt, and the
# failure screenshot shows two bare prompts - the console took the Enter, but
# Ctrl+V never produced anything. pandoc was never started, and the old
# util.file_exists(html_file, 60) (60 polls 10 s apart) then waited 10 minutes
# for a file nobody was writing. The same lost paste hit adobe_acrobatpro.
#
# The conversions take under 10 s once the image is local, so the file is the
# outcome to check. When it has not appeared within `timeout` and no pandoc
# session is running, the command never ran: clear the input line and send it
# again. While a session is still running - a slow download of MANUAL.html -
# keep waiting instead, up to `limit`, so a retry never races a live run
# writing the same file.
def pandoc_convert(args, out_file, attempts=3, timeout=60, limit=600, poll=2):
    command = 'turbo run pandoc --offline --isolate=merge-user' + util.read_extra() + ' -- ' + args
    started = time.time()
    for attempt in range(attempts):
        type(Key.ESC)
        util.paste_text(command, 2)
        type(Key.ENTER)
        sent = time.time()
        while time.time() - started < limit:
            if os.path.exists(out_file):
                return True
            time.sleep(poll)
            if time.time() - sent >= timeout and not pandoc_running():
                break
        if os.path.exists(out_file):
            return True
        Debug.user("pandoc_convert: %s did not appear on attempt %d of %d"
                   % (out_file, attempt + 1, attempts))
        if time.time() - started >= limit:
            break
    return False

def pandoc_running():
    for line in run("turbo sessions -l").splitlines():
        if "pandoc" in line and "Running" in line:
            return True
    return False

# Test turbo run
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
# Convert website to text file
assert(pandoc_convert('-s -r html https://pandoc.org/MANUAL.html -o ' + sample_file, sample_file))
# Convert text file to HTML
assert(pandoc_convert('-s ' + sample_file + ' -o ' + html_file, html_file))
# Convert text file to DOCX
assert(pandoc_convert('-s ' + sample_file + ' -o ' + doc_file, doc_file))
closeApp("Command Prompt")

# Open the converted documents
run("explorer " + sample_file)
wait("txt-sample.png")
closeApp("Notepad")
run("explorer " + os.path.join(util.desktop, "manual.html"))
wait("html-sample.png")
if App("Edge").isRunning(10):
    util.close_app("Edge")
run("explorer " + os.path.join(util.start_menu,"System Tools","Command Prompt.lnk"))
wait(5)
paste('turbo run tdf/libreoffice -d --enable=disablefontpreload' + util.read_extra() + ' -- ' + doc_file)
type(Key.ENTER)
wait(40) # libreoffice crashes on first launch
paste('turbo run tdf/libreoffice -d --enable=disablefontpreload' + util.read_extra() + ' -- ' + doc_file)
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
