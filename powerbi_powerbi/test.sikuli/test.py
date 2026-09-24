# The tests for powerbi/powerbi and powerbi/powerbirs are the same except for the test file path.

script_path = os.path.dirname(os.path.abspath(sys.argv[0])) 
include_path = os.path.join(script_path, os.pardir, os.pardir, "!include", "util.sikuli")
sys.path.append(include_path)
import util
reload(util)
addImagePath(include_path)

setAutoWaitTimeout(30)
util.pre_test()

# Read credentials from the secrets file.
credentials = util.get_credentials(os.path.join(script_path, os.pardir, "resources", "secrets.txt"))
username = credentials.get("username")
password = credentials.get("password")

# Test of `turbo run`.
wait("home_button.png",90)
wait(10)
click(Pattern("close_pbi.png").targetOffset(42,-1))
wait(5)
if exists(Pattern("red_x_click.png").targetOffset(42,1),10):
    click(Pattern("red_x_click.png").targetOffset(42,1))
wait(5)

# Launch the app.
run("explorer " + util.get_shortcut_path_by_prefix(util.desktop, "Power BI Desktop"))
wait("home_button.png",90)
click("sign_in.png")
wait("sign_in_email.png",30)
paste(username)
wait(2)
type(Key.ENTER)
wait("sign_in_email_microsoft.png",30)
paste(username)
wait(2)
type(Key.ENTER)
wait("sign_in_password.png",20)
paste(password)
wait(2)
type(Key.ENTER)
wait("this-app-only.png",20)
click("this-app-only.png")
if exists("sign_in_went_wrong.png",15):
    click("sign_in_continue.png")
if exists("sign_in_done.png",15):
    click("sign_in_done.png")
if exists(Pattern("collaborate_prompt.png").targetOffset(174,-36),15):
    click(Pattern("collaborate_prompt.png").targetOffset(174,-36))

# Basic operations.
click("excel-data.png")
if exists("close-new-feature.png", 15):
    click("close-new-feature.png")
if exists("nothanks.png", 10):
    click("nothanks.png")
wait("import_file_name.png",20)
paste("C:\\Program Files\\Microsoft Power BI Desktop\\bin\\SampleData\\Financial Sample.xlsx")
wait(2)
type(Key.ENTER)
click(Pattern("import_financials.png").targetOffset(-41,-2))
click("import_load.png")
# Load spawns the mashup engine and only then opens the Data pane; on a slow
# pool VM that took longer than the 30 s auto-wait (CI run 33849047386).
wait("data_financials.png", 90)
click(Pattern("data_financials.png").targetOffset(-40,2))
click(Pattern("data_details.png").targetOffset(-45,-14))
click(Pattern("data_details.png").targetOffset(-45,10))
wait(5)
if exists("green-x.png", 15):
    click("green-x.png")
click("transform_data.png")
click("close_apply.png")

# Check "help".
# Start from no Edge at all, so that any msedge.exe seen after the click is the
# one the click launched (see below). Anything that refuses to stop even when
# forced is recorded and ignored.
edge_before = util.stop_processes("msedge.exe")
click("menu_help.png")
# SABOTAGE PROBE: hover instead of click, i.e. a lost Support click.
hover("help_support.png")
# SABOTAGE PROBE: start a windowless fake msedge.exe (ping.exe copied and started
# hidden). Passed as -EncodedCommand: a .ps1 written from here lands in the
# sikulixide sandbox (merge-user isolation) where powershell cannot see it.
import base64
probe_script = (r"$d = Join-Path $env:TEMP 'probe-edge'; New-Item -ItemType Directory -Force $d | Out-Null; "
                r"Copy-Item C:\Windows\System32\PING.EXE (Join-Path $d 'msedge.exe') -Force; "
                r"Start-Process -FilePath (Join-Path $d 'msedge.exe') -ArgumentList '-n','900','127.0.0.1' -WindowStyle Hidden")
run("powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand " + base64.b64encode(probe_script.encode("utf-16-le")))
wait(5)
probe_fake = util.list_processes("msedge.exe")
Debug.user("PROBE: fake msedge.exe spawned; msedge.exe now %s" % probe_fake)
# Help > Support hands the URL to the Edge that the isolate-edge-wc layer brings
# into the container, so the 20 s budget had to cover a browser cold start, the
# navigation and a redirect. It did not. Both tests failed here in App Tests run
# 35678863980 on two different VMs of the same host minutes apart, and in both
# the FAILED frame -- taken in the except handler, ~9 s past the deadline -- shows
# the support page fully rendered and scoring 0.8697 against the reference, i.e.
# the page arrived, just late. The pair had passed the same step on the same xvm
# build 6 h earlier (run 35654098667) with ~19 s of that 20 s already spent, so
# the budget was one slow host away from failing every time. Same shape as the
# acrobatpro F1 wait and the opensearch green-open wait, so use the same helper:
# it re-asserts the focus each round, which also covers Edge opening behind the
# Power BI window, and the close_app below then acts on a focused Edge.
#
# help_url.png is re-captured at the same time. It had read
# ".../en-US/support/" since 2024-06-11, but that path now 302s to "/support/",
# so what kept the step green was the shared prefix of a URL the page no longer
# shows: 0.8697 against the rendered page, down from the 1.0 it was captured at
# and eroding with every further change to the URL. The new reference is cropped
# from this run's lossless -fail.png and scores 1.0 on both failures (0.44 next
# best elsewhere on the screen, 0.44 on the pre-Edge frame, so it still cannot
# pass before the page is up).
#
# App Tests run 35935367711 failed here a second way, with the whole 90 s spent
# and Edge never on screen at all: every frame from the click to the FAILED one
# is the same Power BI window with Support hovered, and the taskbar never shows
# an Edge window. In a passing run Power BI starts msedge.exe itself about 2.5 s
# after the click (VM logs of run 36031259455: "msedge.exe --single-argument
# https://go.microsoft.com/fwlink/?linkid=855944", parent PBIDesktop.exe), so
# 90 s without a window is not a slow start, and which of two things went wrong
# decides what to do about it:
#
# - no new msedge.exe at all: the click never reached the launch. That is the
#   test's problem, so click Help > Support again, up to twice.
# - a new msedge.exe but no Edge window: the launch happened and the browser
#   did not come up inside the container. That is a VM failure, and clicking
#   again would only hide it, so do not retry; fail with a message that says so
#   and leave the processes running for whoever looks at the VM.
#
# The first click gets 50 s (the slowest cold start measured was ~30 s), each
# retry 40 s. Once a click's msedge.exe has appeared it gets 40 s more, i.e. the
# full 90 s #234 allowed a started browser, before its missing window counts.
# A window that is up with the page still not matching is neither case and
# fails at the wait() below, as before.
edge_seen = {}
for click_round in range(3):
    if click_round:
        Debug.user("powerbi: no msedge.exe started after Help > Support; clicking it again (retry %d of 2)" % click_round)
        App("Power BI Desktop").focus()
        if not exists("help_support.png", 5):
            click("menu_help.png")
        click("help_support.png")
    opened = util.wait_launched_window("Edge", "help_url.png", "msedge.exe", edge_before, edge_seen,
                                       attempts=5 if click_round == 0 else 4)
    Debug.user("PROBE: click round %d opened=%s seen=%s" % (click_round, opened, edge_seen))
    if click_round == 0:
        assert not opened, "PROBE control: Edge opened without a Support click"
    if not opened and edge_seen:
        opened = util.wait_launched_window("Edge", "help_url.png", "msedge.exe", edge_before, edge_seen, attempts=4)
    if opened or edge_seen:
        break
# "Window" means an Edge browser window, whose title ends "- Microsoft Edge".
# tasklist also reports the hidden helper windows Edge's other processes own
# (OleMainThreadWndName, OLEChannelWnd), which say nothing about the browser.
edge_window = any("Microsoft" in title and title.endswith("Edge") for title in edge_seen.values())
if not opened and edge_seen and not edge_window:
    alive = util.list_processes("msedge.exe")
    Debug.user("VM FAILURE: msedge.exe started after Help > Support but never opened a window; "
               "new pids %s, still running %s" % (sorted(edge_seen), sorted(p for p in edge_seen if p in alive)))
    assert False, "VM failure: msedge.exe started (pids %s) but no Edge window came up" % sorted(edge_seen)
if not opened:
    if edge_seen:
        Debug.user("powerbi: Edge window up but help_url.png does not match; msedge.exe %s" % edge_seen)
    else:
        Debug.user("powerbi: no msedge.exe started after 3 Help > Support clicks")
    wait("help_url.png", 5)
Debug.user("powerbi: support page up; new msedge.exe %s"
           % dict((p, t) for p, t in util.list_processes("msedge.exe").items() if p not in edge_before))
util.close_app("Edge")
wait(10)
type(Key.F4, Key.ALT)
click("close_no_save.png")
wait(20)

# Check if the session terminates. Power BI Desktop is a large application whose
# windowless children (the Analysis Services engine, WebView2) can outlive the main
# window well past the default 60 s budget: the session still showed Running after
# all 12 polls in App Tests runs 33676687141 and 33849047386 although the window was
# already gone. Allow 36 x 5 s = 3 min; the polls return as soon as the session exits.
util.check_running(max_retries=36)
