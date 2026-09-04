# The tests for microsoft/office-o365business-x64 and microsoft/office-o365proplus-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)

util.pre_test()

# Microsoft renamed the sign-in field label from "Email, phone, or Skype" to
# "Email or phone" and is rolling the change out gradually, so a given VM still
# gets either one - which is why this test fails at whichever
# sign-in-username.png wait it happens to reach first and passes on the VMs that
# still serve the old dialog. sign-in-username.png carries the old label and
# sign-in-username-2.png the new one; match whichever is on screen. Both crops
# are the same size and start at the same left edge as the field, so the click
# offsets below are unchanged.
def find_signin_username(timeout=60):
    for _ in range(max(1, timeout // 2)):
        for image in ("sign-in-username.png", "sign-in-username-2.png"):
            match = exists(image, 1)
            if match:
                return match
    return None

# Click into the email field and enter the username. The dialog keeps rendering
# after the field first appears, so text placed from the first sighting is
# sometimes dropped and Enter then submits an empty field - the dialog comes back
# with "Please enter a valid email address or phone number". Both labels are the
# field placeholder rather than a caption above it, so they disappear as soon as
# the field actually holds a value: use that to confirm the text landed, and
# retry if it did not.
def enter_signin_username(username, timeout=60):
    for attempt in range(3):
        box = find_signin_username(timeout if attempt == 0 else 15)
        if box is None:
            return False
        click(box.getTarget().offset(75, 2))
        wait(1)
        type(username)
        wait(2)
        if find_signin_username(2) is None:
            type(Key.ENTER)
            return True
    return False

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run` and log in. The Office identity outlives the app, so a VM
# that has signed in before comes up already authenticated and shows no Sign In
# button at all - it goes straight to the notebook picker. Waiting for the
# button unconditionally fails there, so only run the sign-in steps if it shows.
if exists("sign-in.png",120):
    type(Key.F4, Key.ALT)
    click("office-sign-in.png")
    if not enter_signin_username(username, 60):
        raise FindFailed("could not enter the sign-in username")
    # The password page is skipped when the credentials are already cached, so
    # it is conditional too; on a cold VM it does appear and 20 s was tight.
    if exists("office_signin_password.png",60):
        paste(password)
        wait(2)
        type(Key.ENTER)
    if exists("office-all-apps.png",10):
        click("office-all-apps.png")
    if exists("device-reg-done.png",15):
        click("device-reg-done.png")
    if exists("office_signin_wrong.png",10):
        type(Key.ENTER)
    if exists("office_signin_all_set.png",10):
        type(Key.ENTER)
    if exists("privacy-close.png",10):
        click("privacy-close.png")
run("turbo stop test")

# OneNote.
run("explorer " + os.path.join(util.start_menu, "OneNote.lnk"))
if exists("sign-in.png",15):
    click("sign-in.png")
enter_signin_username(username, 20)
if exists("sign-in-email-address.png",10):
    click("sign-in-email-address.png")
    wait(3)
    click(Pattern("sign-in-email-address.png").targetOffset(47,2))
    paste(username)
    wait(2)
    type(Key.ENTER)
if exists("continue.png",10):
    click("continue.png")
if exists("office-sign-in.png",10):
    click("office-sign-in.png")
    if not enter_signin_username(username, 60):
        raise FindFailed("could not enter the sign-in username")
if exists("office_signin_password.png",10):
    paste(password)
    wait(2)
    type(Key.ENTER)
if exists("privacy-close.png",10):
    click("privacy-close.png")
wait("onenote-launched.png",30)
if exists("notebooks-cancel.png",30):
    click("notebooks-cancel.png")

wait("new-section.png",20)
wait(10)

# Remove default-named sections left behind by an earlier run. The test creates a
# section and then renames it to "Test"; a run that dies between those two steps
# leaves "New Section 1" behind, and the cleanup at the end only deletes the
# sections it named. The notebook lives in the cloud and is shared by every run
# on every machine, so the leftover is still there for the next run, where it
# shifts the sidebar under the section images and the delete steps act on the
# wrong row. Clear them so the sidebar starts in a known state.
for _ in range(5):
    if not exists("leftover-section.png",5):
        break
    # The sidebar collapses its Recent and Favourites blocks shortly after the
    # notebook opens, which moves every row up, so re-locate immediately before
    # the right-click instead of reusing the first sighting.
    wait(2)
    leftover = exists("leftover-section.png",3)
    if not leftover:
        break
    rightClick(leftover)
    if not exists("delete-note.png",10):
        # Not the section menu - the notebook menu has no Delete entry. Back out
        # rather than clicking anything in a menu we did not mean to open.
        type(Key.ESC)
        wait(2)
        continue
    click("delete-note.png")
    wait("yes-delete.png",20)
    click("yes-delete.png")
    wait(5)

click("new-section.png")
wait(5)
paste("Test")
wait(2)
type(Key.TAB)
paste("Test")
wait(2)
type(Key.TAB)
paste("first line")
wait(2)
type(Key.ENTER)
paste("second line")
wait(2)
type(Key.ENTER)
paste("third line")
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
wait("onenote_result_1.png",60)

click(Pattern("onenote_menu.png").targetOffset(-88,1))
click("onenote_table.png")
wait(2)
click(Pattern("onenote_table_menu.png").targetOffset(-24,-12))
wait("onenote_table_insert.png",10)
type(Key.ENTER)
wait("onenote_result_2.png",10)

click(Pattern("onenote_menu.png").targetOffset(-88,1))
click("onenote_pictures.png")
wait(2)
click(Pattern("onenote_pictures_menu.png").targetOffset(-9,-27))
wait("onenote_file_name.png",20)
paste(os.path.join(script_path, os.pardir, "resources", "red fox.jpg"))
wait(2)
type(Key.ENTER)
wait("onenote_result_3.png",20)
wait(5)
type("p", Key.CTRL)
wait("onenote_print.png",20)
type(Key.ESC)
wait("onenote_result_3.png",10)
if exists("quick-notes-notebook.png",10):
    rightClick("quick-notes-notebook.png")
    click("delete-note.png")
    # the confirmation dialog is not instant; clicking blind misses it
    wait("yes-delete.png",20)
    click("yes-delete.png")
    wait(5)
if exists("test-section2.png",10):
    rightClick("test-section2.png")
    click("delete-note.png")
    # the confirmation dialog is not instant; clicking blind misses it
    wait("yes-delete.png",20)
    click("yes-delete.png")
    wait(5)
if exists("test-section.png",10):
    rightClick("test-section.png")
    click("delete-note.png")
    # the confirmation dialog is not instant; clicking blind misses it
    wait("yes-delete.png",20)
    click("yes-delete.png")
    wait(5)
type(Key.F1)
# The help pane loads its content over the network and intermittently comes back
# with "Sorry, we cannot load this feature ... Click Retry once you are back
# online." The pane itself is up at that point, so retry rather than fail.
if not exists("onenote_help.png",30):
    if exists("help_retry.png",5):
        click("help_retry.png")
    wait("onenote_help.png",60)
wait(20) # Wait for syncing.

type(Key.F4, Key.ALT)
os.system('cmd /c taskkill /f /im "smartscreen.exe" /t')
wait(20)

# Check if the session terminates.
util.check_running()