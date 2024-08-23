# Common operations used in app test scripts.

from sikuli import *

# Useful paths.
desktop = os.path.join((os.environ["USERPROFILE"]), "Desktop")
start_menu = os.path.join((os.environ["APPDATA"]), "Microsoft", "Windows", "Start Menu", "Programs")

# Operations before running app test.
def pre_test():
    # Workaround for the bug that when Num-Lock is on, Key.SHIFT does not work with arrow keys: https://answers.launchpad.net/sikuli/+question/143874.
    if Env.isLockOn(Key.NUM_LOCK):
        type(Key.NUM_LOCK)

    # OneDrive shortcut should not be captured.
    assert(not os.path.exists(os.path.join(start_menu, "OneDrive (2).lnk")))

    # Hide the SikuliX java window.
    java_cmd = App().focus("java")
    if java_cmd.isValid():
        type(Key.DOWN, Key.WIN)

# Get credentials from secrets.txt. That secret file locates under the "resources" folder of the app script folder.
def get_credentials(path):
    credentials = {}
 
    with open(path, "r") as file:
        lines = file.readlines()
        for line in lines:
            key, value = line.strip().split(",")
            credentials[key] = value

    return credentials

# Log in for Adobe Creative Cloud.
def adobe_cc_login(username, password):
    wait("adobe_login.png", 90)
    click(Pattern("adobe_login.png").targetOffset(-193,13))
    type(username)
    click(Pattern("adobe_login_continue.png").similar(0.90))
    wait("adobe_login_pass.png", 90)
    click(Pattern("adobe_login_pass.png").targetOffset(-184,8))
    type(password)
    click(Pattern("adobe_login_continue.png").similar(0.90))
    if exists("adobe_login_signout_others.png", 15):
        click(Pattern("adobe_login_signout_others.png").targetOffset(2,55))
        click(Pattern("adobe_login_continue.png").similar(0.90))

# Get the path of the shortcut for the apps that have different shortcut names for different versions.
# Assume there is only one match inside the folder.
def get_shortcut_path_by_prefix(folder_path, prefix):
    files = os.listdir(folder_path)
    matching = [file for file in files if file.startswith(prefix)]
    return os.path.join(folder_path, matching[0])

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
def close_firewall_alert():
    activate_app_window("Windows Security Alert",200)
    wait("firewall.png")

    click(Pattern("firewall.png").targetOffset(212,67))

# Close the Windows firewall alert prompt. Continue if not prompted after 60 seconds.
def close_firewall_alert_continue():
    activate_app_window("Windows Security Alert",200)
    if exists("firewall.png"):
        click(Pattern("firewall.png").targetOffset(212,67))

# Check if the most recently created Turbo session is terminated.
# It is usually the session for the app to be tested.
def check_running():
    assert("Running" not in run("turbo sessions -l"))
