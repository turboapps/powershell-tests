# PROBE ONLY - raise a Windows notification banner over the system tray corner.
#
# scenario="reminder" is what makes it stay put instead of fading after a few
# seconds, which is how the Windows Security "Turn on Windows Firewall" banner
# in App Tests run 35063712843 was still covering the tray flyout when the test
# reached its right-click. A reminder toast requires an action, so it also gets
# the same Dismiss button the real one had.
$ErrorActionPreference = 'Stop'

$appId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'

[void][Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime]
[void][Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom, ContentType = WindowsRuntime]

$xml = @'
<toast scenario="reminder">
  <visual>
    <binding template="ToastGeneric">
      <text>Probe</text>
      <text>Standing in for the Windows Security banner of run 35063712843.</text>
    </binding>
  </visual>
  <actions>
    <action content="Dismiss" arguments="dismiss" activationType="foreground"/>
  </actions>
</toast>
'@

$doc = New-Object Windows.Data.Xml.Dom.XmlDocument
$doc.LoadXml($xml)
$toast = New-Object Windows.UI.Notifications.ToastNotification $doc
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show($toast)
Write-Output 'probe toast raised'
