script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

pdf_path = os.path.join(script_path, os.pardir, "resources", "sample.pdf")
save_path =  os.path.join(util.desktop, "sample.pdf")

setAutoWaitTimeout(50)
util.pre_test()

# Foxit 2026.2.0 opens a "Translate Document" suggestion in the notification
# panel, and that panel overlays the sticky note the comment step clicks, so
# comment_box.png could no longer be found (CI runs 33676687141 and its rerun
# 33700259173 both died there; 2026.1.3 passed). Clear the notification
# whenever it is showing. The panel is anchored to the note, so "Clear" is
# clicked at a fixed offset from the message text.
def dismiss_translate_notification():
    notification = Pattern("translate-notification.png")
    if exists(notification, 2):
        click(notification.targetOffset(-143, -63))
        wait(1)

# Select the title word and highlight it.
#
# This used to be two blind doubleClicks ("Need to do this twice.") followed by
# the Highlight click, with nothing checking that a word had actually been
# selected. In App Tests run 33949816065 nothing was: the step frames show
# "Sample" with no selection where the passing run of the same commit
# (33949826631, same app build 2026.2.0.39747) shows it boxed in blue, and the
# SikuliX log has the two doubleClicks landing 81 ms apart - close enough for
# Windows to chain all four clicks into one sequence and collapse the selection.
# The Highlight click then only armed the tool, the yellow highlight never
# appeared, and the test died 50 s later at text_sample_highlighted.png with
# nothing in the failure pointing at the selection.
#
# So settle between the doubleClicks - each is then an independent double-click
# rather than half of a four-click sequence - and retry the selection while it is
# still free to retry, which means before the Highlight click. Highlight is what
# mutates the layout: it opens the Format side panel, and closing that panel
# leaves a collapsed rail behind, so fit-width recomputes to 163.85% instead of
# the 165.56% every reference was captured at. That ~1% scale error is not
# something template matching can absorb (measured on probe run 34090311224), so
# there is no way back once Highlight has been clicked.
#
# The settle has a useful side effect: it gives Foxit time to raise its selection
# mini-toolbar over the word, which is a far better "is anything selected" signal
# than the selection itself. The blue fill differs from unselected text by colour
# alone and SikuliX's normalised correlation barely sees it (0.99 unselected vs
# 1.00 selected), whereas the toolbar scores 1.00 present against 0.22 absent
# across all four runs measured. It is still only used to decide whether to
# double-click again, never to fail: the toolbar does not appear at all without
# the settle, so treat a miss as inconclusive and let the highlight check below -
# the assertion that actually matters - have the final say.
def highlight_sample_word(attempts=3, settle=20):
    for attempt in range(attempts):
        for _ in range(2):
            doubleClick(Pattern("pdf_sample.png").targetOffset(-182,-63))
            wait(1)   # let the double-click chain expire before the next click
        if exists("text_sample_selected.png", 2):
            break
        Debug.user("highlight_sample_word: no selection toolbar after attempt %d of %d"
                   % (attempt + 1, attempts))
    click("highlight-tool.png")
    # Fail here, fast and saying why, rather than 50 s later at an image three
    # steps downstream of the actual problem.
    if not exists(Pattern("text_sample_highlighted.png").similar(0.60), settle):
        raise FindFailed("highlight_sample_word: clicked Highlight but no highlight "
                         "appeared - the doubleClick did not select the word")

# Test of `turbo run`.
wait("foxit_window.png")
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "Foxit PDF Reader", "Foxit PDF Reader.lnk"))
wait("foxit_window.png")
type("o", Key.CTRL)
click(Pattern("open_location.png").targetOffset(20,-4))
paste(pdf_path)
type("o", Key.ALT)
if exists("next-button.png",30):
    click("next-button.png")
    type(Key.ESC)
wait("pdf_sample.png")
dismiss_translate_notification()
highlight_sample_word()
# Click beside the new annotation to deselect it, so result_1.png (the highlight
# without its selection handles) can match on the next line.
click(Pattern("text_sample_highlighted.png").similar(0.60).targetOffset(104,-10))
wait(Pattern("result_1.png").similar(0.60))
type("n", Key.CTRL + Key.SHIFT)
wait("comment_ready.png")
click(Pattern("result_1.png").similar(0.60).targetOffset(79,-16))
dismiss_translate_notification()
click(Pattern("comment_box.png").targetOffset(-1,10))
paste("test")
type(Key.ESC)
wait(Pattern("result_2.png").similar(0.60))
type("s", Key.CTRL + Key.SHIFT)
wait("save_location.png")
paste(save_path)
type(Key.ENTER)
assert(util.file_exists(save_path, 5))
type(Key.F4, Key.ALT)
wait("sample-pdf-desktop.png")
rightClick("sample-pdf-desktop.png")
click("open-with.png")
click("choose-another-app.png")
click("open-with-foxit-reader.png")
click("always.png")
type(Key.ENTER)
wait(Pattern("foxit_opened.png").similar(0.60))
wait(5)
click("foxit_opened.png")
type(Key.F4, Key.ALT)
run("explorer " + save_path)
wait(Pattern("foxit_opened.png").similar(0.60))
wait(5)
type(Key.F4, Key.ALT)
wait(20)

# Check if the session terminates.
util.check_running()
