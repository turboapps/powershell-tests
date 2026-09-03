# Common operations used in app test scripts.
from sikuli import *

# Useful paths.
desktop = os.path.join((os.environ["USERPROFILE"]), "Desktop")
start_menu = os.path.join((os.environ["APPDATA"]), "Microsoft", "Windows", "Start Menu", "Programs")

# Operations before running app test.
def pre_test(no_min=False):
    # Workaround for the bug that when Num-Lock is on, Key.SHIFT does not work with arrow keys: https://answers.launchpad.net/sikuli/+question/143874.
    if Env.isLockOn(Key.NUM_LOCK):
        type(Key.NUM_LOCK)

    # OneDrive shortcut should not be captured.
    assert(not os.path.exists(os.path.join(start_menu, "OneDrive (2).lnk")))

# Get credentials from secrets.txt. That secret file locates under the "resources" folder of the app script folder.
def get_credentials(path):
    credentials = {}
 
    with open(path, "r") as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split(",")
            credentials[key] = value

    return credentials

# Launch Adobe Creative Cloud
def launch_adobe_cc(username, password):
    run('turbo installi creativeclouddesktop --network=test --enable=usedllinjection --isolate=merge --offline')
    run("explorer " + get_shortcut_path_by_prefix(start_menu, "Adobe Creative Cloud"))
    activate_app_window("Creative Cloud Desktop",30)
    adobe_cc_login(username, password)
    wait(15)
    type("w", Key.CTRL)
    wait(5)
    closeApp("Creative Cloud Desktop")

# Log in for Adobe Creative Cloud.
def adobe_cc_login(username, password):
    wait(Pattern("adobe_login.png").similar(0.40),60)
    click("cancel-button.png")
    wait(20)
    wait(Pattern("adobe_login.png").similar(0.40),10)
    click(Pattern("adobe_login.png").similar(0.40))
    wait(3)
    paste(username)
    wait(3)
    type(Key.ENTER)
    wait(Pattern("adobe_login_pass.png").similar(0.40),15)
    wait(3)
    click(Pattern("adobe_login_pass.png").similar(0.40))
    wait(3)
    paste(password)
    wait(3)
    type(Key.ENTER)
    if exists("adobe_login_signout_others.png",15):
        click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
        click(Pattern("adobe_login_continue.png").similar(0.80))
    if exists("adobe_login_team.png"):
        click(Pattern("adobe_login_continue.png").similar(0.80))

# Get the path of the shortcut for the apps that have different shortcut names for different versions.
# Assume there is only one match inside the folder.
def get_shortcut_path_by_prefix(folder_path, prefix):
    files = os.listdir(folder_path)
    matching = [file for file in files if file.startswith(prefix)]
    return os.path.join(folder_path, matching[0])

# Launch an app from its installed shortcut, given every name it is known by.
#
# Two naming schemes are in play, and which one applies depends on the image,
# not on the test. When the captured installer created Start Menu shortcuts of
# its own (any MSI/EXE app), the client replays those, so the shortcut keeps
# the vendor's name and subfolder ("Zoom\Zoom Workplace.lnk"). When the
# installer created none (a ZIP app such as Temurin), the client synthesizes a
# single flat shortcut from the image Title ("Temurin JDK LTS ARM64.lnk").
# Passing both candidates keeps a test working under either, and across a
# rebuild that changes which one an image produces.
#
# Each candidate is relative to `base` (the Start Menu by default): a string
# for a flat shortcut, or a list of segments for one inside a subfolder.
#
# Resolve before launching, because run("explorer <missing path>") does not
# fail - Explorer silently opens a "Documents" window and the test dies later
# at an unrelated wait(), pointing at the wrong thing. Raise here instead, and
# list what is actually installed so the real name is in the log.
def launch_shortcut(*candidates, **kwargs):
    base = kwargs.get("base", start_menu)
    tried = []
    for candidate in candidates:
        parts = list(candidate) if isinstance(candidate, (list, tuple)) else [candidate]
        path = os.path.join(base, *parts)
        tried.append(path)
        if os.path.exists(path):
            run("explorer " + path)
            return path
    raise AssertionError(
        "No shortcut found for this app.\nTried:\n  %s\nInstalled under %s:\n  %s"
        % ("\n  ".join(tried), base, "\n  ".join(list_shortcuts(base)) or "(nothing)"))

# List the shortcuts under a folder, two levels deep, relative to it.
# Used to report what is really installed when launch_shortcut finds nothing.
def list_shortcuts(base):
    found = []
    if not os.path.exists(base):
        return found
    for entry in sorted(os.listdir(base)):
        full = os.path.join(base, entry)
        if os.path.isdir(full):
            for child in sorted(os.listdir(full)):
                found.append(os.path.join(entry, child))
        else:
            found.append(entry)
    return found

# Given a partial file name and path find the file and return the path.
# Useful for searching for a shortcut that changes names eg. PowerBI RS.
def find_file(folder_path, partial_name):
    # Check if the folder path exists.
    if not os.path.exists(folder_path):
        return None   
    # Iterate over files in the folder.
    for file_name in os.listdir(folder_path):
        # Check if the partial name is in the file name.
        if partial_name in file_name:
            # Return the full path of the first matching file.
            return os.path.join(folder_path, file_name) 
    # If no matching file is found, return None.
    return None

# Check if a file exists. It checks every 10 seconds unitl `try_limit` is reached.
def file_exists(path, try_limit):
    tried = 0
    while tried < try_limit:
        if os.path.exists(path):
            return True
        tried += 1
        time.sleep(10)
    return False

# Activate app window named (windowName) - will attempt for (numAttempts) seconds
def activate_app_window(windowName, numAttempts):
    for attempt in range(numAttempts):
        app_window = App().focus(windowName)
        if app_window.isValid():
            return True
        else:
            wait(1)

# Close the Windows firewall alert prompt.
def close_firewall_alert(wait_time = 200):
    activate_app_window("Windows Security Alert", wait_time)
    wait("firewall.png")
    click(Pattern("firewall.png").targetOffset(95,29))
# Close the Windows firewall alert prompt. Continue if not prompted after 60 seconds.
def close_firewall_alert_continue(wait_time = 200):
    activate_app_window("Windows Security Alert", wait_time)
    if exists("firewall.png"):
        click(Pattern("firewall.png").targetOffset(95,29))

# Check if the most recently created Turbo session is terminated.
# It is usually the session for the app to be tested.
def check_running(max_retries=12, delay=5):
    for attempt in range(max_retries):
        output = run("turbo sessions -l")
        if "Running" not in output:
            return
        time.sleep(delay)
    assert "Running" not in output
