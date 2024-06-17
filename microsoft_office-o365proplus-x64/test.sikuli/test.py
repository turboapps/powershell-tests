script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(45)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait(120)
click(Pattern("office_signin.png").targetOffset(-114,106))
wait("office_signin_email.png")
type(username + Key.ENTER)
wait("office_signin_password.png")
type(password + Key.ENTER)
wait("office_signin_all_apps.png")
type(Key.ENTER)
if exists("office_signin_wrong.png"):
    type(Key.ENTER)
else:
    wait("office_signin_all_set.png")
    type(Key.ENTER)
wait("word_window_not_selected.png")
type(Key.F4, Key.ALT)
run("turbo stop test")


# Word.
word_save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "First line.docx")
run("explorer " + os.path.join(util.start_menu, "Word.lnk"))
if exists("office_signin.png"):
    click(Pattern("office_signin.png").targetOffset(-114,106))
    wait("office_signin_email.png")
    type(username + Key.ENTER)
wait("word_window_not_selected.png")
wait("word_window.png")
wait(10) # Wati for "Get the office ready for you".
click("word_window.png")

wait("word_new_doc.png")
type("first line" + Key.ENTER)
type("second line" + Key.ENTER)
type("third line" + Key.ENTER)
type("fourth line")
type(Key.HOME, Key.CTRL) # Move the cursor to the start of the document.
type(Key.DOWN, Key.SHIFT) # Select the whole line.
type("b", Key.CTRL) # Bold text.
type(Key.RIGHT) # Move the cursor to the next line.
type(Key.DOWN, Key.SHIFT)
type("i", Key.CTRL) # Italic text.
type(Key.RIGHT)
type(Key.DOWN, Key.SHIFT)
click(Pattern("word_paragraph_menu.png").targetOffset(-103,-30))
type(Key.RIGHT)
type(Key.DOWN, Key.SHIFT)
click(Pattern("word_paragraph_menu.png").targetOffset(-63,-30))
type(Key.RIGHT)
wait("word_result_1.png")

type(Key.ENTER + Key.ENTER)
click(Pattern("word_menu.png").targetOffset(-69,0))
click(Pattern("word_insert_menu.png").targetOffset(-55,-13))
click(Pattern("word_insert_table_menu.png").targetOffset(-24,-52))
click(Pattern("word_insert_table_window.png").targetOffset(-11,99))
wait("word_result_2.png")

click(Pattern("word_menu.png").targetOffset(-69,0))
click(Pattern("word_insert_menu.png").targetOffset(0,-13))
wait(2)
click(Pattern("word_insert_picture_menu.png").targetOffset(-2,-13))
wait("word_file_name.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("word_result_3.png")

click(Pattern("word_menu.png").targetOffset(-63,0))
click(Pattern("word_insert_menu.png").targetOffset(55,-13))
click(Pattern("word_insert_shape_menu.png").targetOffset(-109,42))
dragDrop(Pattern("word_result_1.png").targetOffset(-57,-46), Pattern("word_result_1.png").targetOffset(33,45))
wait("word_result_4.png")

type("s", Key.CTRL)
click(Pattern("word_save.png").targetOffset(-7,8))
click(Pattern("word_save_location.png").targetOffset(-81,29))
click(Pattern("word_save_save.png").targetOffset(-41,0))
wait(5)
assert(os.path.exists(word_save_location))
type("w", Key.CTRL)
run("explorer " + word_save_location)
wait("word_result_5.png")

type("p", Key.CTRL)
wait("word_print.png")
type(Key.ESC)
wait("word_result_5.png")

type(Key.F1)
wait("word_help.png")
type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates.
util.check_running()


# PowerPoint.
save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "Title.pptx")

run("explorer " + os.path.join(util.start_menu, "PowerPoint.lnk"))
click("ppt_window.png")
if exists("ppt_not_now.png"):
    click(Pattern("ppt_not_now.png").targetOffset(43,-3))
if exists("ppt_got_it.png"):
    click(Pattern("ppt_got_it.png").targetOffset(35,2))
if exists("ppt_designer.png"):
    click(Pattern("ppt_designer.png").targetOffset(120,-13))

click("ppt_title_subtitle_1.png")
type("Title")
click("ppt_title_subtitle_2.png")
type("Subtitle")
wait("ppt_title_subtitle_3.png")

click(Pattern("ppt_new_slide.png").targetOffset(0,20))
click("ppt_new_slide_menu.png")
click(Pattern("ppt_slide_created.png").targetOffset(-148,47))
type("first line" + Key.ENTER)
type("second line" + Key.ENTER)
type("third line")
type(Key.HOME, Key.CTRL) # Move the cursor to the start of the document.
type(Key.DOWN, Key.SHIFT) # Select the whole line.
type("b", Key.CTRL) # Bold text.
type(Key.RIGHT) # Move the cursor to the next line.
type(Key.DOWN, Key.SHIFT)
type("i", Key.CTRL) # Italic text.
type(Key.RIGHT)
type(Key.DOWN, Key.SHIFT)
type("u", Key.CTRL) # Underline text.
type(Key.RIGHT)
wait("ppt_result_1.png")

type(Key.ENTER + Key.ENTER)
click(Pattern("ppt_menu.png").targetOffset(55,0))
click("ppt_table.png")
wait(2)
click(Pattern("ppt_table_menu.png").targetOffset(-11,-25))
wait("ppt_table_insert.png")
type(Key.ENTER)
wait("ppt_result_2.png")

click(Pattern("ppt_menu.png").targetOffset(55,0))
click("ppt_pictures.png")
wait(2)
click(Pattern("ppt_pictures_menu.png").targetOffset(-2,-13))
wait("ppt_file_name.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("ppt_result_3.png")

type("s", Key.CTRL)
click("ppt_save.png")
click(Pattern("ppt_save_location.png").targetOffset(-78,23))
click(Pattern("ppt_save_save.png").targetOffset(-38,1))
wait(5)
assert(os.path.exists(save_location))
type("w", Key.CTRL)
run("explorer " + save_location)
wait("ppt_result_4.png")

type("p", Key.CTRL)
wait("ppt_print.png")
type(Key.ESC)
wait("ppt_result_4.png")

type(Key.F1)
wait("ppt_help.png")

type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates.
util.check_running()


# Excel.
save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "Book1.xlsx")

run("explorer " + os.path.join(util.start_menu, "Excel.lnk"))
click("excel_window.png")
wait("excel_new_document.png")
type("1" + Key.ENTER)
type("2" + Key.ENTER)
type("=sum(A1, A2)" + Key.ENTER)
wait("excel_result.png")

type("s", Key.CTRL)
click(Pattern("excel_save.png").targetOffset(0,-35))
click(Pattern("excel_save_location.png").targetOffset(-96,31))
click(Pattern("excel_save_save.png").targetOffset(-41,2))
wait(5)
assert(os.path.exists(save_location))
type("w", Key.CTRL)
run("explorer " + save_location)
wait("excel_result.png")
type("w", Key.CTRL)
run("explorer " +os.path.join(script_path, os.pardir, "resources", "csv.csv"))
wait("excel_csv.png")

type("p", Key.CTRL)
wait("excel_print.png")
type(Key.ESC)
wait("excel_csv.png")

type(Key.F1)
wait("excel_help.png")

type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates.
util.check_running()


# OneNote.
run("explorer " + os.path.join(util.start_menu, "OneNote.lnk"))
click("onenote_not_now.png")
wait(10)
click("onenote_add_page.png")
wait(2)
type("Test" + Key.TAB)
type("first line" + Key.ENTER)
type("second line" + Key.ENTER)
type("third line")
type(Key.HOME, Key.CTRL) # Move the cursor to the start of the document.
type(Key.DOWN, Key.SHIFT) # Select the whole line.
type("b", Key.CTRL) # Bold text.
type(Key.RIGHT) # Move the cursor to the next line.
type(Key.DOWN, Key.SHIFT)
type("i", Key.CTRL) # Italic text.
type(Key.RIGHT)
type(Key.DOWN, Key.SHIFT)
type("u", Key.CTRL) # Underline text.
type(Key.RIGHT)
wait("onenote_result_1.png")

click(Pattern("onenote_menu.png").targetOffset(-98,1))
click("onenote_table.png")
wait(2)
click(Pattern("onenote_table_menu.png").targetOffset(-24,-12))
wait("onenote_table_insert.png")
type(Key.ENTER)
wait("onenote_result_2.png")

click(Pattern("onenote_menu.png").targetOffset(-98,1))
click("onenote_pictures.png")
wait(2)
click(Pattern("onenote_pictures_menu.png").targetOffset(-9,-27))
wait("onenote_file_name.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("onenote_result_3.png")

click(Pattern("onenote_menu.png").targetOffset(-98,1))
click("onenote_file.png")
wait("onenote_file_name.png")
if exists("onenote_warning.png"):
    click(Pattern("onenote_warning.png").targetOffset(138,94))
type(os.path.join(script_path, os.pardir, "resources", "csv.csv") + Key.ENTER)
click(Pattern("onenote_file_attach.png").targetOffset(-28,-25))
wait("onenote_result_4.png")

type("p", Key.CTRL)
wait("onenote_print.png")
type(Key.ESC)
wait("onenote_result_4.png")

type(Key.F1)
wait("onenote_help.png")

rightClick("onenote_page.png")
click("onenote_page_menu.png")
wait(15) # Wait for syncing.

type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates.
util.check_running()


# Access.
save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "Database1.accdb")

run("explorer " + os.path.join(util.start_menu, "Access.lnk"))
click("access_window.png")
click(Pattern("access_create.png").targetOffset(-71,66))
click(Pattern("access_add_column_1.png").targetOffset(46,-4))
click(Pattern("access_type.png").targetOffset(-5,-57))
wait("access_add_column_2.png")
type("Fruit" + Key.ENTER)
click(Pattern("access_type.png").targetOffset(-5,28))
wait("access_add_column_3.png")
type("Price" + Key.ENTER)
wait(2)
type(Key.ESC)
click(Pattern("access_add_row.png").targetOffset(-54,14))
type("Apple" + Key.ENTER)
type("1" + Key.ENTER + Key.TAB)
type("Pear" + Key.ENTER)
type("2" + Key.ENTER)
wait("access_result_1.png")

type("s", Key.CTRL)
wait("access_save.png")
type(Key.ENTER)
assert(os.path.exists(save_location))
type(Key.F4, Key.ALT)
run("explorer " + save_location)
click("access_open_enable.png")
doubleClick("access_open_table1.png")
wait("access_result_2.png")


type("p", Key.CTRL)
wait("access_print.png")
type(Key.ESC)
wait("access_result_2.png")

type(Key.F1)
wait("access_help.png")

type(Key.F4, Key.ALT)
wait(30)

# Check if the session terminates.
util.check_running()


# Publisher.
save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "Publication1.pub")

run("explorer " + os.path.join(util.start_menu, "Publisher.lnk"))
click("publisher_window.png")
wait("publisher_new_file.png")
click("publisher_draw_text_box.png")
dragDrop(Pattern("publisher_new_file.png").targetOffset(-257,-14), Pattern("publisher_new_file.png").targetOffset(3,78))
wait("publisher_result_1.png")
type("first line" + Key.ENTER)
type("second line" + Key.ENTER)
type("third line")
type(Key.HOME, Key.CTRL) # Move the cursor to the start of the document.
type(Key.DOWN, Key.SHIFT) # Select the whole line.
type("b", Key.CTRL) # Bold text.
type(Key.RIGHT) # Move the cursor to the next line.
type(Key.DOWN, Key.SHIFT)
type("i", Key.CTRL) # Italic text.
type(Key.RIGHT)
type(Key.DOWN, Key.SHIFT)
type("u", Key.CTRL) # Underline text.
type(Key.RIGHT)
type(Key.F9)
wait("publisher_result_2.png")

type(Key.ENTER + Key.ENTER)
click(Pattern("publisher_menu.png").targetOffset(-122,0))
click("publisher_table.png")
wait(2)
click("publisher_table_menu.png")
wait("publisher_table_insert.png")
type(Key.ENTER)
wait("publisher_result_3.png")

click(Pattern("publisher_menu.png").targetOffset(-122,0))
click("publisher_pictures.png")
wait(2)
wait("publisher_file_name.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("publisher_result_4.png")

type("s", Key.CTRL)
click(Pattern("publisher_save.png").targetOffset(0,56))
wait("publisher_save_location.png")
type(save_location + Key.ENTER)
wait(5)
assert(os.path.exists(save_location))
type(Key.F4, Key.ALT)
wait(5)
run("explorer " + save_location)
click(Pattern("publisher_saved_file.png").targetOffset(-202,130))

type("p", Key.CTRL)
wait("publisher_print.png")
wait(15) # Wait for the preview to load.
type(Key.ESC)
wait("publisher_saved_file.png")

type(Key.F1)
wait("publisher_help.png")

type(Key.F4, Key.ALT)
click(Pattern("publisher_save_changes.png").targetOffset(35,32))
wait(30)

# Check if the session terminates.
util.check_running()


# Outlook.
run("explorer " + os.path.join(util.start_menu, "Outlook.lnk"))
click(Pattern("outlook_add_account_1.png").targetOffset(-4,138))
click(Pattern("outlook_add_account_2.png").targetOffset(-200,16)) # Get focus.
click(Pattern("outlook_add_account_2.png").targetOffset(-182,-12))
click(Pattern("outlook_add_account_2.png").targetOffset(1,16))
click(Pattern("outlook_outlook_window.png").similar(0.90).targetOffset(26,-43))
wait("outlook_compose.png")
wait(15) # For the task bar popup.
type(username + Key.TAB + Key.TAB + Key.TAB)
type("subject" + Key.TAB)
type("content")
click("outlook_send.png")

click(Pattern("outlook_new_email_1.png").similar(0.80))
wait("outlook_new_email_2.png")
type("p", Key.CTRL)
wait("outlook_print.png")
type(Key.ESC)
wait("outlook_new_email_2.png")
type(Key.DELETE)

type(Key.F1)
wait("outlook_help.png")

type(Key.F4, Key.ALT)
wait(60)

# Check if the session terminates.
util.check_running()