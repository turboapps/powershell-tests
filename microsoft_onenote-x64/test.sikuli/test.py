# The tests for microsoft/office-o365business-x64 and microsoft/office-o365proplus-x64 are the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
import time
addImagePath(include_path)

setAutoWaitTimeout(30)

util.pre_test()

# The Microsoft account sign-in page names its username field only through the
# field's placeholder, and Microsoft keeps rewriting that placeholder - and
# sometimes does not draw it at all. Three wordings have been seen so far, each
# with its own crop, all 163x25 and all taken from the field's own text row so
# the click offset below is the same for every one of them:
#
#   sign-in-username.png    "Email, phone, or Skype"
#   sign-in-username-2.png  "Email or phone"
#   sign-in-username-3.png  "Email or phone, including Gmail and iCloud"
#
# and in App Tests run 35654098667 the field came up with no placeholder at all
# - an empty, focused box that never gained one in the 60 s the step allowed.
# That run died at the first sign-in and run 35678863980 died at the one after
# the relaunch on the third wording, both of them spending a full budget
# hunting for placeholders that were not on screen.
#
# So do not depend on the placeholder to find the field. The page's "Sign in"
# heading is the same on all of those variants and sits at a fixed distance
# above the field. sign-in-heading.png carries it with the rest of its line, and
# the empty line matters: the "Sign in to all apps and websites on this device?"
# page that follows the password opens with the same two words in the same face,
# and a crop of the words alone matches it at 0.98. Measured over the 185 step
# frames of both runs, the full-line crop scores 0.98-1.00 on every sign-in page
# and at most 0.48 anywhere else - the all-apps page, the password page, the
# Office activation page, the notebook - so it names this one page. Use a
# placeholder when one is on screen, because it points straight at the field,
# and fall back to the heading when none is.
SIGNIN_PLACEHOLDERS = ("sign-in-username.png", "sign-in-username-2.png", "sign-in-username-3.png")

def on_signin_username_page(timeout=1):
    if exists("sign-in-heading.png", timeout):
        return True
    for image in SIGNIN_PLACEHOLDERS:
        if exists(image, 0):
            return True
    return False

def find_signin_field(timeout=60):
    """Where to click to put the caret in the sign-in username field."""
    started = time.time()
    while True:
        for image in SIGNIN_PLACEHOLDERS:
            match = exists(image, 0)
            if match:
                return match.getTarget().offset(75, 2)
        heading = exists("sign-in-heading.png", 0)
        if heading:
            # Measured on the run 35678863980 frames: the heading crop centres
            # on (919,378) and the field's text row on (937,439), 13 px above
            # the underline that closes the box.
            return heading.getTarget().offset(18, 61)
        if time.time() - started >= timeout:
            return None
        wait(1)

# Click into the email field and enter the username. The dialog keeps rendering
# after the field first appears, so text placed from the first sighting is
# sometimes dropped and Enter then submits an empty field - the dialog comes back
# with "Please enter a valid email address or phone number". Confirm the username
# landed by watching for the page to stop asking for one, which holds whatever
# the placeholder says; the old check - placeholder gone, so the text is in -
# could not tell an accepted username from a placeholder that was never drawn.
#
# Nothing here selects the field's contents before typing. An earlier draft
# pressed Ctrl+A first, so that a retry would replace a half-typed value rather
# than append to it, and probe run 35776082425 showed what that costs: the click
# did not focus the field, so Ctrl+A selected the whole sign-in page instead, and
# the select-all highlight inverted the heading and every other anchor on it. The
# page then read as gone, the step reported a username it had never entered, and
# the run died 90 s later at new-section.png. The value being replaced was
# hypothetical - a dropped attempt leaves the field empty, which is the case on
# record - and the check below is what a real one would need anyway.
def enter_signin_username(username, timeout=60):
    for attempt in range(3):
        target = find_signin_field(timeout if attempt == 0 else 15)
        if target is None:
            return False
        click(target)
        wait(1)
        type(username)
        wait(2)
        type(Key.ENTER)
        # Give the page 30 s to move on: it goes to the password page when the
        # username was taken, and stays put - with an error, or with the field
        # exactly as it was - when the click never reached the field or Enter
        # submitted an empty one. Either way the next attempt re-locates the
        # field and clicks it again, which is also what clears a first click
        # that only woke the dialog's window instead of focusing anything in it.
        #
        # Read the page as gone only when two checks in a row agree. A single
        # miss is not enough: anything that repaints the page over the anchors
        # reads exactly like the page having moved on, and that is a silent
        # false pass - the run carries on unauthenticated and dies much later
        # somewhere unrelated.
        gone = 0
        for _ in range(15):
            if exists("office_signin_password.png", 0):
                Debug.user("enter_signin_username: password page on attempt %d" % (attempt + 1))
                return True
            if on_signin_username_page(1):
                gone = 0
                continue
            gone += 1
            if gone >= 2:
                Debug.user("enter_signin_username: accepted on attempt %d" % (attempt + 1))
                return True
        Debug.user("enter_signin_username: page still asking after attempt %d" % (attempt + 1))
    return False

# --- The navigation pane ------------------------------------------------
#
# OneNote greys the whole navigation pane out while it is still opening
# notebooks and silently drops clicks on it, and a greyed "+ New Section" link
# still matches new-section.png at 0.88 against the 0.7 threshold - so waiting
# for that image is not a readiness check at all. App Tests run 35787162482
# cleared the wait on a disabled pane, clicked a link that did nothing, and then
# typed the section name into the page title and the note body, where OneNote's
# Tab turns a paragraph into a table. That table, holding the three lines the
# test meant to put on a page, is what sits in the middle of every
# onenote_result_1.png failure - 90 s after the click that caused it. The pane
# says in as many words that it is busy, so wait for that to go instead.
def wait_notebooks_loaded(timeout=180):
    started = time.time()
    # The message takes a moment to appear after the notebook prompt is
    # answered, so a single miss proves nothing; want it gone three times over.
    quiet = 0
    while time.time() - started < timeout:
        if exists("notebooks-loading.png", 1):
            quiet = 0
        else:
            quiet += 1
            if quiet >= 3:
                return True
        wait(1)
    Debug.user("wait_notebooks_loaded: pane still loading after %d s" % (time.time() - started))
    return False

# Every section this test makes goes in My Notebook, the notebook OneNote keeps
# on the machine under Documents\OneNote Notebooks. It belongs to the VM, so two
# runs on two VMs cannot see each other's sections. The account's cloud notebook
# is the opposite - every run on every machine shares it - and a bare
# click("new-section.png") takes whichever "+ New Section" link scores highest,
# which is the cloud notebook's whenever it happens to be open. Anchor every
# section step on My Notebook's own row instead, so the notebook is never in
# doubt, sections another run left in the cloud notebook only move rows this
# test no longer looks at, and nothing here can delete a section another run is
# working on.
def topmost(region, image):
    """The highest match of image within region, or None. Region.exists() gives
    the best-scoring match rather than the first one, which is no use when the
    point is to tell one notebook's rows from another's."""
    try:
        matches = list(region.findAll(image))
    except FindFailed:
        return None
    if not matches:
        return None
    return min(matches, key=lambda match: match.y)

def my_notebook_region():
    """Every sidebar row from My Notebook's own row down."""
    row = exists("my-notebook.png", 30)
    if row is None:
        return None
    top = row.getTarget().y + 12
    return Region(0, top, 200, SCREEN.getH() - top)

def my_notebook_new_section():
    """My Notebook's "+ New Section" link. It closes that notebook's rows, so
    within the region it is the topmost one even when another notebook is
    listed below."""
    region = my_notebook_region()
    if region is None:
        return None
    return topmost(region, "new-section.png")

def my_notebook_sections():
    """The rows between My Notebook and its "+ New Section" link - that
    notebook's sections and nothing else."""
    region = my_notebook_region()
    if region is None:
        return None
    link = topmost(region, "new-section.png")
    if link is None:
        return None
    height = link.y - region.y
    if height <= 0:
        return None
    return Region(region.x, region.y, region.w, height)

def delete_section(row):
    """Right-click a section row and delete it, backing out if the menu that
    opens is not a section's."""
    rightClick(row)
    if not exists("delete-note.png", 10):
        # Not the section menu - a notebook's has no Delete entry. Back out
        # rather than clicking anything in a menu we did not mean to open.
        type(Key.ESC)
        wait(2)
        return False
    click("delete-note.png")
    # the confirmation dialog is not instant; clicking blind misses it
    wait("yes-delete.png", 20)
    click("yes-delete.png")
    wait(5)
    return True

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

# The relaunched OneNote settles into one of two states: its "Getting things
# ready for you!" card with a Sign In button, or - on a VM whose Office identity
# survived the restart - the notebook itself. Which one it is decides whether
# the sign-in steps below have any work to do, so resolve it by waiting for
# whichever appears rather than polling the card on a fixed budget.
#
# The card is slow to paint and its arrival straddles the 15 s this step used to
# allow: it came up ~10 s after the launch in App Tests run 35063712843 (pass)
# and ~15 s in run 35063730062 (fail), where exists("sign-in.png",15) gave up
# about a second before the card appeared. Missing it is silent and fatal, not
# merely a lost click: every check below is a post-sign-in surface, so they all
# fall through, and the run dies 90 s later at onenote-launched.png with the
# Sign In card still sitting on screen, never clicked - a failure that points at
# the wrong step entirely.
#
# The two images separate the states cleanly, so neither can stand in for the
# other: on the card, sign-in.png scores 0.91 and onenote-launched.png 0.44; in
# the notebook it is 0.34 and 0.91 the other way (measured on the step frames of
# those two runs, against a 0.7 threshold). The launched state is checked too so
# that an already-authenticated VM costs nothing instead of the full budget.
def wait_onenote_start(timeout=120):
    started = time.time()
    for _ in range(max(1, timeout // 2)):
        for image, state in (("sign-in.png", "sign-in"), ("onenote-launched.png", "launched")):
            if exists(image, 1):
                Debug.user("wait_onenote_start: %s after %d s" % (state, time.time() - started))
                return state
    Debug.user("wait_onenote_start: neither state after %d s" % (time.time() - started))
    return None

if wait_onenote_start() == "sign-in":
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

wait_notebooks_loaded()
wait("new-section.png",20)
wait(10)

# Remove default-named sections left behind by an earlier run on this VM. The
# test creates a section and then renames it to "Test"; a run that dies between
# those two steps leaves "New Section 1" behind, and the cleanup at the end only
# deletes the sections it named.
#
# Look for them only among My Notebook's own section rows. leftover-section.png
# is "New Section 1" and the link below those rows reads "+ New Section", which
# it matches at 0.87-0.95 - so searching the whole screen finds the link, every
# time, in runs that have no leftover at all: the loop then right-clicks it five
# times over and backs out of a menu with no Delete in it. Cutting the search off
# above the link removes the false match without touching the image.
for _ in range(5):
    sections = my_notebook_sections()
    if sections is None:
        break
    if not sections.exists("leftover-section.png", 5):
        break
    # The sidebar collapses its Recent and Favourites blocks shortly after the
    # notebook opens, which moves every row up, so re-locate immediately before
    # the right-click instead of reusing the first sighting.
    wait(2)
    sections = my_notebook_sections()
    leftover = sections and sections.exists("leftover-section.png", 3)
    if not leftover:
        break
    delete_section(leftover)

# Make the section. Clicking "+ New Section" opens an inline rename editor in
# the sidebar with the default name selected, and the paste below goes into it;
# the Tab after that commits the name and moves on to the page title. When the
# click does not take, none of that is true and the same keystrokes go into the
# page and build a table instead, so wait for the editor and click again rather
# than trusting a fixed budget.
for attempt in range(3):
    link = my_notebook_new_section()
    if link is None:
        raise FindFailed("My Notebook has no New Section link")
    click(link)
    if exists("section-rename.png", 15):
        break
    Debug.user("new section: no rename editor on attempt %d" % (attempt + 1))
    wait(5)
else:
    raise FindFailed("clicking New Section did not open the rename editor")
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
# Delete only this VM's own sections. Matched against the whole screen these
# names find the cloud notebook's rows just as readily - it has a "Quick Notes"
# of its own, and a "Test" left by any run that died before its cleanup - so a
# run could delete a section another run was working on.
for image in ("quick-notes-notebook.png", "test-section2.png", "test-section.png"):
    sections = my_notebook_sections()
    if sections is None:
        break
    row = sections.exists(image, 10)
    if row:
        delete_section(row)
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