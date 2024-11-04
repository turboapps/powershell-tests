# The tests for microsoft/office-o365business-x64 and microsoft/office-o365proplus-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(60)

util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run` and log in.
wait(60)
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
save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "First line.docx")

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
click(Pattern("word_paragraph_menu.png").targetOffset(-102,-16))
type(Key.RIGHT)
type(Key.DOWN, Key.SHIFT)
click(Pattern("word_paragraph_menu.png").targetOffset(-60,-15))
type(Key.RIGHT)
wait("word_result_1.png")

type(Key.ENTER + Key.ENTER)
click(Pattern("word_menu.png").targetOffset(-61,1))
click(Pattern("word_insert_menu.png").targetOffset(-53,-15))
click(Pattern("word_insert_table_menu.png").targetOffset(-22,-53))
click(Pattern("word_insert_table_window.png").targetOffset(-11,99))
wait("word_result_2.png")

click(Pattern("word_menu.png").targetOffset(-61,1))
click(Pattern("word_insert_menu.png").targetOffset(4,-15))
wait(2)
click(Pattern("word_insert_picture_menu.png").targetOffset(-5,-26))
wait("word_file_name.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("word_result_3.png")

click(Pattern("word_menu.png").targetOffset(-61,1))
click(Pattern("word_insert_menu.png").targetOffset(54,-8))
click(Pattern("word_insert_shape_menu.png").targetOffset(-111,39))
dragDrop(Pattern("word_result_1.png").targetOffset(-57,-46), Pattern("word_result_1.png").targetOffset(33,45))
wait("word_result_4.png")

type("s", Key.CTRL)
click(Pattern("word_save.png").targetOffset(-118,11))
click(Pattern("word_save_location.png").targetOffset(-29,28))
click(Pattern("word_save_save.png").targetOffset(-38,-2))
assert(util.file_exists(save_location, 5))
type("w", Key.CTRL)
run("explorer " + save_location)
wait("word_result_5.png")

type("p", Key.CTRL)
wait("word_print.png")
type(Key.ESC)
wait("word_result_5.png")

type(Key.F1)
wait("word_help.png")
type(Key.F4, Key.ALT)
wait(45)

# Check if the session terminates.
util.check_running()


# PowerPoint.
save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "Title.pptx")

run("explorer " + os.path.join(util.start_menu, "PowerPoint.lnk"))
wait("ppt_window.png")
wait(2)
click("ppt_window.png")
if exists("ppt_choose_theme.png"):
    click(Pattern("ppt_choose_theme_ok.png").targetOffset(43,2))
if exists("ppt_got_it.png"):
    click("ppt_got_it.png")
if exists("ppt_designer.png"):
    click(Pattern("ppt_designer.png").targetOffset(152,-14))

click("ppt_title_subtitle_1.png")
type("Title")
click("ppt_title_subtitle_2.png")
type("Subtitle")
wait("ppt_title_subtitle_3.png")

click(Pattern("ppt_new_slide.png").targetOffset(0,20))
click("ppt_new_slide_menu.png")
if exists("ppt_got_it.png"):
    click("ppt_got_it.png")
click(Pattern("ppt_slide_created.png").targetOffset(-175,49))
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
click(Pattern("ppt_menu_1.png").targetOffset(50,0))
if exists("ppt_got_it.png"):
    click("ppt_got_it.png")
click("ppt_table.png")
wait(2)
click(Pattern("ppt_table_menu.png").targetOffset(-11,-25))
wait("ppt_table_insert.png")
type(Key.ENTER)
wait("ppt_result_2.png")

click(Pattern("ppt_menu_2.png").targetOffset(48,1))
click("ppt_pictures.png")
wait(2)
click(Pattern("ppt_pictures_menu.png").targetOffset(-2,-13))
wait("ppt_file_name.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("ppt_result_3.png")

type("s", Key.CTRL)
click("ppt_save.png")
click(Pattern("ppt_save_location.png").targetOffset(-17,25))
click(Pattern("ppt_save_save.png").targetOffset(-40,-1))
assert(util.file_exists(save_location, 5))
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
wait(45)

# Check if the session terminates.
util.check_running()


# Excel.
save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "Book1.xlsx")

run("explorer " + os.path.join(util.start_menu, "Excel.lnk"))
wait("excel_window.png")
wait(2)
click("excel_window.png")
wait("excel_new_document.png")
type("1" + Key.ENTER)
type("2" + Key.ENTER)
type("=sum(A1, A2)" + Key.ENTER)
wait("excel_result.png")

type("s", Key.CTRL)
click("excel_save.png")
click(Pattern("excel_save_location.png").targetOffset(-19,25))
click(Pattern("excel_save_save.png").targetOffset(-42,-2))
assert(util.file_exists(save_location, 5))
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
wait(45)

# Check if the session terminates.
util.check_running()


# OneNote.
run("explorer " + os.path.join(util.start_menu, "OneNote.lnk"))
click("onenote_not_now.png")
wait(10)
wait("onenote_add_page.png")
wait(2)
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

click(Pattern("onenote_menu.png").targetOffset(-88,1))
click("onenote_table.png")
wait(2)
click(Pattern("onenote_table_menu.png").targetOffset(-24,-12))
wait("onenote_table_insert.png")
type(Key.ENTER)
wait("onenote_result_2.png")

click(Pattern("onenote_menu.png").targetOffset(-88,1))
click("onenote_pictures.png")
wait(2)
click(Pattern("onenote_pictures_menu.png").targetOffset(-9,-27))
wait("onenote_file_name.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("onenote_result_3.png")

click(Pattern("onenote_menu.png").targetOffset(-88,1))
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
wait(20) # Wait for syncing.

type(Key.F4, Key.ALT)
wait(45)

# Check if the session terminates.
util.check_running()


# Access.
save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "Database1.accdb")

run("explorer " + os.path.join(util.start_menu, "Access.lnk"))
wait("access_window.png")
wait(2)
click("access_window.png")
click(Pattern("access_create.png").targetOffset(-71,66))
click(Pattern("access_add_column_1.png").targetOffset(46,0))
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
assert(util.file_exists(save_location, 5))
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
wait(45)

# Check if the session terminates.
util.check_running()


# Publisher.
save_location = os.path.join((os.environ["USERPROFILE"]), "Documents", "Publication1.pub")

run("explorer " + os.path.join(util.start_menu, "Publisher.lnk"))
wait("publisher_window.png")
wait(2)
click("publisher_window.png")
wait(Pattern("publisher_new_file.png").similar(0.80))
click("publisher_draw_text_box.png")
dragDrop(Pattern("publisher_new_file.png").similar(0.80).targetOffset(-257,-14), Pattern("publisher_new_file.png").similar(0.80).targetOffset(3,78))
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
click(Pattern("publisher_menu.png").targetOffset(-117,0))
click("publisher_table.png")
wait(2)
click("publisher_table_menu.png")
wait("publisher_table_insert.png")
type(Key.ENTER)
wait("publisher_result_3.png")

click(Pattern("publisher_menu.png").targetOffset(-117,0))
click("publisher_pictures.png")
wait(2)
wait("publisher_file_name.png")
type(os.path.join(script_path, os.pardir, "resources", "red fox.jpg") + Key.ENTER)
wait("publisher_result_4.png")

type("s", Key.CTRL)
click(Pattern("publisher_save.png").targetOffset(0,61))
wait("publisher_save_location.png")
type(save_location + Key.ENTER)
wait(5)
assert(util.file_exists(save_location, 5))
type(Key.F4, Key.ALT)
wait(5)
run("explorer " + save_location)
wait(Pattern("publisher_saved_file.png").targetOffset(-202,130))

type("p", Key.CTRL)
wait("publisher_print.png")
wait(15) # Wait for the preview to load.
type(Key.ESC)
wait("publisher_saved_file.png")

type(Key.F1)
wait("publisher_help.png")

type(Key.F4, Key.ALT)
click(Pattern("publisher_save_changes.png").targetOffset(32,27))
wait(45)

# Check if the session terminates.
util.check_running()


# Outlook.
run("explorer " + os.path.join(util.start_menu, "Outlook (classic).lnk"))
click(Pattern("outlook_add_account_1.png").targetOffset(0,6))
click(Pattern("outlook_add_account_2.png").targetOffset(-198,13)) # Get focus.
click(Pattern("outlook_add_account_2.png").targetOffset(-182,-14))
click(Pattern("outlook_add_account_2.png").targetOffset(0,14))

if exists("outlook_got_it.png",30):
    click("outlook_got_it.png")
if exists("outlook_got_it.png",15):
    click("outlook_got_it.png")
click("outlook_new_email.png")
if exists("outlook_got_it.png",15):
    click("outlook_got_it.png")
wait("outlook_compose.png")
wait(15) # For the task bar popup.
type(username + Key.TAB)
wait(1)
type(Key.TAB + Key.TAB)
type("subject" + Key.TAB)
wait(1)
type("content")
click("outlook_send.png")

click("outlook_new_email_1.png")
wait("outlook_new_email_2.png")
type("p", Key.CTRL)
wait("outlook_print.png")
type(Key.ESC)
wait("outlook_new_email_2.png")
type(Key.DELETE)
wait(15)

type(Key.F1)
wait("outlook_help.png")

type(Key.F4, Key.ALT)
wait(60)

# Check if the session terminates.
util.check_running()