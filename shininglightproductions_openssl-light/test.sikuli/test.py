# The tests for shininglightproductions/openssl and shininglightproductions/openssl-light are basically the same.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(20)
util.pre_test(no_min=True)

# Minimize the sikulix console
if exists("sikulix-console.png",15):
    click("sikulix-console.png")
    wait(2)
    type(Key.DOWN, Key.WIN)

# Test of `turbo run` and command line mode.
wait("openssl-cmd-prompt.png")
type("openssl help" + Key.ENTER)
wait("openssl-help-cmd.png")
wait(3)
run("turbo stop test")

# Launch the app.
run("explorer " + os.path.join(util.start_menu, "OpenSSL", "Win64 OpenSSL Command Prompt.lnk"))
wait("openssl-cmd-prompt.png")

# Basic operations.
certInFile = os.path.join(script_path, os.pardir, "resources", "certificate.pfx")
certOutFile = os.path.join(util.desktop, "certificate.pem")
openSSLcmd = "openssl pkcs12 -in " + certInFile + " -out " + certOutFile + " -nodes"
type(openSSLcmd + Key.ENTER)
wait("enter-password.png")
type("thisismycertpassword" + Key.ENTER)
wait(5)
assert(util.file_exists(certOutFile, 10))
with open(certOutFile, 'r') as file:
    content = file.read()
    assert("-----END PRIVATE KEY-----" in content)
type("exit" + Key.ENTER)
wait(5)

# Test headless trigger.
certOutFile = os.path.join(util.desktop, "headless_cert.pem")
headlessCmd = "turbo run openssl-light --isolate=merge-user --trigger headless -- pkcs12 -in " + certInFile + " -out " + certOutFile + " -nodes -password pass:thisismycertpassword"
run(headlessCmd)
wait(5)
assert(util.file_exists(certOutFile, 10))
with open(certOutFile, 'r') as file:
    content = file.read()
    assert("-----END PRIVATE KEY-----" in content)


# Check if the session terminates.
util.check_running()