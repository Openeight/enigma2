from stat import ST_MTIME
from time import *
from Plugins.Extensions.ExtrasPanel.plugin import *

config.plugins.dvbntptime = ConfigSubsection()
config.misc.useTransponderTime = ConfigBoolean(default=True)
config.plugins.dvbntptime.ntpautocheck = ConfigYesNo(default=False)
config.plugins.dvbntptime.tdtautocheck = ConfigYesNo(default=False)
config.plugins.dvbntptime.enablemainmenu = ConfigYesNo(default=False)
config.plugins.dvbntptime.showntpmessage = ConfigYesNo(default=False)
showmessage = _('Show NTP message on startup') + ': '
ntpautostart = _('NTP-Server autostart') + ': '
tdtautostart = _('DVB Time check autostart') + ': '
transponderupdate = _('Enigma 2 Time update') + ': '

class XTDVBNTPTime(Screen):
    skin = """
    <screen name="XTDVBNTPTime" position="center,center" size="700,500" title="DVB NTP Time menu">
        <ePixmap pixmap="skin_default/buttons/button_red.png" position="48,372" size="15,16" alphatest="on" />
        <ePixmap pixmap="skin_default/buttons/button_green.png" position="48,421" size="15,16" alphatest="on" />
        <ePixmap pixmap="skin_default/buttons/button_yellow.png" position="392,372" size="15,16" alphatest="on" />
        <ePixmap pixmap="skin_default/buttons/button_blue.png" position="392,419" size="15,16" alphatest="on" />
        <widget name="key_red" position="72,364" zPosition="1" size="241,37" font="Regular;17" halign="left" valign="center" transparent="1" />
        <widget name="key_green" position="72,413" zPosition="1" size="241,37" font="Regular;17" halign="left" valign="center" transparent="1" />
        <widget name="key_yellow" position="420,364" zPosition="1" size="241,37" font="Regular;17" halign="left" valign="center" transparent="1" />
        <widget name="key_blue" position="420,413" zPosition="1" size="241,37" font="Regular;17" halign="left" valign="center" transparent="1" />        
        <widget source="menu" render="Listbox" position="48,25" size="610,260" zPosition="3" scrollbarMode="showNever">
                <convert type="TemplatedMultiContent">
                    {"template": [
                            MultiContentEntryText(pos = (10, 5), size = (608, 26), flags = RT_HALIGN_LEFT, text = 1), # index 0 is the MenuText,
                        ],
                    "fonts": [gFont("Regular", 22)],
                    "itemHeight": 35
                    }
            </convert>
        </widget>
        <widget source="menu" render="Listbox" position="48,230" size="610,250" zPosition="3" scrollbarMode="showNever" selectionDisabled="1" transparent="1">
            <convert type="TemplatedMultiContent">
                {"template": [
                        MultiContentEntryText(pos = (0, 0), size = (610, 250), flags = RT_HALIGN_CENTER|RT_VALIGN_TOP|RT_WRAP, text = 2), # index 0 is the MenuText,
                    ],
                "fonts": [gFont("Regular", 19)],
                "itemHeight": 250
                }
            </convert>
        </widget>
    </screen>"""
    def __init__(self, session, args = 0):
        self.skin = XTDVBNTPTime.skin
        self.session = session
        Screen.__init__(self, session)
        NetworkConnectionAvailable = None
        self.menu = args
        self.list = []
        self.list.append(('XTDVBNTPTimecheck', _('Check DVB Time'), _('This option is to check manually if there is a time difference between current system time and the transponder time.')))
        self.list.append(('XTDVBNTPTimeset', _('Set DVB Time'), _('This option sets the time from the current transponder as system time.')))
        self.list.append(('XTDVBNTPTimesetforced', _('Forced set DVB Time'), _('Setting the DVB Time forced is only needed if the check shows a time difference of more then 30 min.\nATTENTION: With forced option make an Enigma 2 restart at the finish !')))
        self.list.append(('changetime', _('Set system time manually'), _('This option is to set the system time manually with the remote control.')))
        self.list.append(('checkntptime', _('Check and set with NTP-Server'), _('Compare the system time with a central time server and set the new system time.')))
        self['menu'] = List(self.list)
        self['key_red'] = Label(showmessage)
        self['key_green'] = Label(ntpautostart)
        self['key_yellow'] = Label(tdtautostart)
        self['key_blue'] = Label(transponderupdate)
        self['actions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'ok': self.go,
         'exit': self.keyCancel,
         'back': self.keyCancel,
         'red': self.switchshowmessage,
         'green': self.autostartntpchecknetwork,
         'yellow': self.switchtdt,
         'blue': self.onoffautotrans}, -1)
        self.onShown.append(self.updateSettings)
        self.onLayoutFinish.append(self.layoutFinished)
        self.onShown.append(self.setWindowTitle)

    def updateSettings(self):
        showmessage_state = showmessage
        ntpautostart_state = ntpautostart
        tdtautostart_state = tdtautostart
        transponderupdate_state = transponderupdate
        if config.plugins.dvbntptime.showntpmessage.value:
            showmessage_state += _('On')
        else:
            showmessage_state += _('Off')
        if config.plugins.dvbntptime.ntpautocheck.value:
            ntpautostart_state += _('On')
        else:
            ntpautostart_state += _('Off')
        if config.plugins.dvbntptime.tdtautocheck.value:
            tdtautostart_state += _('On')
        else:
            tdtautostart_state += _('Off')
        if config.misc.useTransponderTime.value:
            transponderupdate_state += _('On')
        else:
            transponderupdate_state += _('Off')
        self['key_red'].setText(showmessage_state)
        self['key_green'].setText(ntpautostart_state)
        self['key_yellow'].setText(tdtautostart_state)
        self['key_blue'].setText(transponderupdate_state)

    def layoutFinished(self):
        idx = 0
        self['menu'].index = idx

    def setWindowTitle(self):
        self.setTitle(_('DVB NTP Time menu'))

    def go(self):
        current = self['menu'].getCurrent()
        if current:
            currentEntry = current[0]
            if self.menu == 0:
                if currentEntry == 'XTDVBNTPTimecheck':
                    self.session.open(Console, _('Checking DVB Time...'), ['/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/dvbdate --print'])
                elif currentEntry == 'XTDVBNTPTimeset':
                    if config.misc.useTransponderTime.value == True:
                        self.session.open(MessageBox, _('Set DVB Time not useful,switch off Enigma 2 Timeupdate first !'), MessageBox.TYPE_INFO, timeout=10)
                    elif config.plugins.dvbntptime.ntpautocheck.value:
                        self.session.open(MessageBox, _('NTP-Server autostart is enabled,please switch off first !'), MessageBox.TYPE_INFO, timeout=10)
                    else:
                        self.DoSetXTDVBNTPTime(True)
                elif currentEntry == 'XTDVBNTPTimesetforced':
                    if config.plugins.dvbntptime.ntpautocheck.value:
                        self.session.open(MessageBox, _('NTP-Server autostart is enabled,please switch off first !'), MessageBox.TYPE_INFO, timeout=10)
                    elif config.misc.useTransponderTime.value == True:
                        self.session.open(MessageBox, _('Forced set DVB Time not useful,switch off Enigma 2 Timeupdate first !'), MessageBox.TYPE_INFO, timeout=10)
                    else:
                        self.DoSetXTDVBNTPTimeforce(True)
                elif currentEntry == 'checkntptime':
                    if config.misc.useTransponderTime.value == True:
                        self.session.open(MessageBox, _('Check and set with NTP-Server not useful,switch off Enigma 2 Timeupdate first !'), MessageBox.TYPE_INFO, timeout=10)
                    else:
                        self.startnetworkcheck()
                elif currentEntry == 'changetime':
                    if config.plugins.dvbntptime.ntpautocheck.value:
                        self.session.open(MessageBox, _('NTP-Server autostart is enabled,please switch off first !'), MessageBox.TYPE_INFO, timeout=10)
                    elif config.misc.useTransponderTime.value == True:
                        self.session.open(MessageBox, _('Set system time manually not useful,switch off Enigma 2 Timeupdate first !'), MessageBox.TYPE_INFO, timeout=10)
                    else:
                        ChangeTimeWizzard(self.session)

    def autostartntpchecknetwork(self, callback = None):
        self.session.open(MessageBox, _('Check Network status.\nPlease wait...'), MessageBox.TYPE_INFO, timeout=10)
        if callback is not None:
            self.NotifierCallback = callback
        iNetwork.checkNetworkState(self.checkNetworkCBautontp)

    def checkNetworkCBautontp(self, data):
        if data is not None:
            if data <= 2:
                XTDVBNTPTime.NetworkConnectionAvailable = True
                self.session.openWithCallback(self.autostartntpcheck, MessageBox, _('Restart Enigma 2 for automatic NTP-Server check on startup (on/off) ?'), MessageBox.TYPE_YESNO)
            else:
                self.session.open(MessageBox, _('Change NTP-Server autostart not not possible:\n\nNetwork status: Unreachable !'), MessageBox.TYPE_ERROR)

    def autostartntpcheck(self, answer):
        if answer is False:
            self.skipXTDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            if config.plugins.dvbntptime.ntpautocheck.value:
                config.plugins.dvbntptime.showntpmessage.setValue(False)
                config.plugins.dvbntptime.ntpautocheck.setValue(False)
                config.misc.useTransponderTime.setValue(True)
            else:
                config.plugins.dvbntptime.ntpautocheck.setValue(True)
                config.plugins.dvbntptime.showntpmessage.setValue(True)
                config.plugins.dvbntptime.tdtautocheck.setValue(False)
                config.misc.useTransponderTime.setValue(False)
            self.updateSettings()
            config.plugins.dvbntptime.ntpautocheck.save()
            config.plugins.dvbntptime.showntpmessage.save()
            config.plugins.dvbntptime.tdtautocheck.save()
            config.misc.useTransponderTime.save()
            self.callRestart(True)

    def onoffautotrans(self):
        self.session.openWithCallback(self.autotransponder, MessageBox, _('Restart Enigma 2 to switch on/off Enigma 2 Timeupdate on startup ?\nATTENTION: When you switch off,all automatic time updates are disabled !!!'), MessageBox.TYPE_YESNO)

    def autotransponder(self, answer):
        if answer is False:
            self.skipXTDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            if config.misc.useTransponderTime.value:
                config.misc.useTransponderTime.setValue(False)
            else:
                config.misc.useTransponderTime.setValue(True)
                config.plugins.dvbntptime.tdtautocheck.setValue(False)
                config.plugins.dvbntptime.ntpautocheck.setValue(False)
                config.plugins.dvbntptime.showntpmessage.setValue(False)
            self.updateSettings()
            config.misc.useTransponderTime.save()
            config.plugins.dvbntptime.tdtautocheck.save()
            config.plugins.dvbntptime.ntpautocheck.save()
            config.plugins.dvbntptime.showntpmessage.save()
            self.callRestartTransponder(True)

    def switchtdt(self):
        self.session.openWithCallback(self.autostarttdtcheck, MessageBox, _('Restart Enigma 2 to display DVB Time check results on startup (on/off) ?'), MessageBox.TYPE_YESNO)

    def autostarttdtcheck(self, answer):
        if answer is False:
            self.skipXTDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            if config.plugins.dvbntptime.tdtautocheck.value:
                config.plugins.dvbntptime.tdtautocheck.setValue(False)
                config.misc.useTransponderTime.setValue(True)
            else:
                config.plugins.dvbntptime.tdtautocheck.setValue(True)
                config.plugins.dvbntptime.ntpautocheck.setValue(False)
                config.plugins.dvbntptime.showntpmessage.setValue(False)
                config.misc.useTransponderTime.setValue(False)
            self.updateSettings()
            config.plugins.dvbntptime.tdtautocheck.save()
            config.plugins.dvbntptime.ntpautocheck.save()
            config.plugins.dvbntptime.showntpmessage.save()
            config.misc.useTransponderTime.save()
            self.callRestart(True)

    def switchMainMenu(self):
        self.session.openWithCallback(self.setMainMenu, MessageBox, _('Restarting Enigma 2 to switch on/off display\nthe DVB Time in the Mainmenu ?'), MessageBox.TYPE_YESNO)

    def setMainMenu(self, answer):
        if answer is False:
            self.skipXTDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            if config.plugins.dvbntptime.enablemainmenu.value:
                config.plugins.dvbntptime.enablemainmenu.setValue(False)
            else:
                config.plugins.dvbntptime.enablemainmenu.setValue(True)
            self.updateSettings()
            config.plugins.dvbntptime.enablemainmenu.save()
            self.callRestart(True)

    def switchshowmessage(self):
        if config.plugins.dvbntptime.ntpautocheck.value == False:
            self.session.open(MessageBox, _('That makes no sense when turned off the auto start from the NTP-Server.\nPlease switch on the autostart first !'), MessageBox.TYPE_INFO, timeout=10)
        else:
            self.session.openWithCallback(self.onoffshowmessage, MessageBox, _('Restarting Enigma 2 to switch on/off\nthe NTP message on startup ?'), MessageBox.TYPE_YESNO)

    def onoffshowmessage(self, answer):
        if answer is False:
            self.skipXTDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            if config.plugins.dvbntptime.showntpmessage.value:
                config.plugins.dvbntptime.showntpmessage.setValue(False)
            else:
                config.plugins.dvbntptime.showntpmessage.setValue(True)
            self.updateSettings()
            config.plugins.dvbntptime.showntpmessage.save()
            self.callRestart(True)

    def callRestart(self, answer):
        if answer is None:
            self.skipXTDVBNTPTimeautostart(_('Reason: Answer is none'))
        if answer is False:
            self.skipXTDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            quitMainloop(3)

    def callRestartTransponder(self, answer):
        if answer is None:
            self.skipXTDVBNTPTimeautostart(_('Reason: Answer is none'))
        if answer is False:
            self.skipXTDVBNTPTimeautostart(_('Reason: Abort by User !'))
        if answer is True:
            quitMainloop(3)

    def skipXTDVBNTPTimeautostart(self, reason):
        self.session.open(MessageBox, _('DVB Time setting aborted:\n\n%s') % reason, MessageBox.TYPE_ERROR)

    def startnetworkcheck(self, callback = None):
        if callback is not None:
            self.NotifierCallback = callback
        iNetwork.checkNetworkState(self.checkNetworkCB)

    def checkNetworkCB(self, data):
        if data is not None:
            if data <= 2:
                XTDVBNTPTime.NetworkConnectionAvailable = True
                self.container = eConsoleAppContainer()
                self.container.appClosed.append(self.finishedntp)
                self.container.execute('ntpdate de.pool.ntp.org tick.fh-augsburg.de time2.one4vision.de')
            else:
                self.session.open(MessageBox, _('NTP check not not possible:\n\nNetwork status: Unreachable !'), MessageBox.TYPE_ERROR)

    def finishedntp(self, retval):
        timenow = strftime('%Y:%m:%d %H:%M', localtime())
        self.session.open(MessageBox, _('NTP-Server check and system time update\nto %s successfully done.') % timenow, MessageBox.TYPE_INFO, timeout=10)

    def DoSetXTDVBNTPTime(self, answer):
        self.container = eConsoleAppContainer()
        self.container.execute('dvbdate --set')
        self.session.openWithCallback(self.finished, MessageBox, _('DVB Time update running.\nPlease wait...'), MessageBox.TYPE_INFO, timeout=10)

    def finished(self, answer):
        if answer is None:
            self.skipXTDVBNTPTime(_('Reason: Answer is none'))
        if answer is False:
            self.skipXTDVBNTPTime(_('Reason: Abort by User !'))
        if answer is True:
            timenow = strftime('%Y:%m:%d %H:%M', localtime())
            self.session.open(MessageBox, _('DVB Time updating to %s\nsuccessfully done.') % timenow, MessageBox.TYPE_INFO, timeout=10)

    def DoSetXTDVBNTPTimeforce(self, answer):
        if answer is None:
            self.skipXTDVBNTPTime(_('Reason: Answer is none'))
        if answer is False:
            self.skipXTDVBNTPTime(_('Reason: Abort by User !'))
        if answer is True:
            self.session.openWithCallback(self.forcefinished, MessageBox, _('Setting DVB Time with forced option.\nWhen finished Enigma 2 restarts automatically !\nPlease wait...'), MessageBox.TYPE_INFO, timeout=30)
            self.container = eConsoleAppContainer()
            self.container.execute('dvbdate --set --force')

    def forcefinished(self, answer):
        if answer is None:
            self.skipXTDVBNTPTime(_('Reason: Answer is none'))
        if answer is False:
            self.skipXTDVBNTPTime(_('Reason: Abort by User !'))
        if answer is True:
            quitMainloop(3)

    def skipXTDVBNTPTime(self, reason):
        self.session.open(MessageBox, _('DVB Time setting aborted:\n\n%s') % reason, MessageBox.TYPE_ERROR)

    def keyCancel(self):
        self.close(None)


class NTPStartup(Screen):
    skin = '\n        <screen position="center,center" size="400,300" title=" " >\n        </screen>'

    def __init__(self, session):
        self.skin = NTPStartup.skin
        self.session = session
        Screen.__init__(self, session)
        NetworkConnectionAvailable = None
        self.TimerXTDVBNTPTimeStartup = eTimer()
        self.TimerXTDVBNTPTimeStartup.stop()
        self.TimerXTDVBNTPTimeStartup.timeout.get().append(self.startnetworkcheckntp)
        self.TimerXTDVBNTPTimeStartup.start(3000, True)

    def startnetworkcheckntp(self, callback = None):
        if callback is not None:
            self.NotifierCallback = callback
        iNetwork.checkNetworkState(self.checkNetworkCBntp)

    def checkNetworkCBntp(self, data):
        if data is not None:
            if data <= 2:
                XTDVBNTPTime.NetworkConnectionAvailable = True
                self.TimerXTDVBNTPTimeStartup.stop()
                self.container = eConsoleAppContainer()
                self.container.appClosed.append(self.finishedntpauto)
                self.container.execute('ntpdate de.pool.ntp.org tick.fh-augsburg.de time2.one4vision.de')
            else:
                self.session.open(MessageBox, _('NTP check not not possible:\n\nNetwork status: Unreachable !'), MessageBox.TYPE_ERROR)

    def finishedntpauto(self, retval):
        if config.plugins.dvbntptime.showntpmessage.value:
            timenow = strftime('%Y:%m:%d %H:%M', localtime())
            print '[XTPanel] Time is: ' + timenow
            self.session.open(MessageBox, _('NTP Time check successfully.\nSystem time set to %s finished.') % timenow, MessageBox.TYPE_INFO, timeout=10)


class XTDVBNTPTimeStartup(Screen):
    skin = '\n        <screen position="center,center" size="400,300" title=" " >\n        </screen>'

    def __init__(self, session):
        self.skin = XTDVBNTPTimeStartup.skin
        self.session = session
        Screen.__init__(self, session)
        self.TimerXTDVBNTPTimeStartup = eTimer()
        self.TimerXTDVBNTPTimeStartup.stop()
        self.TimerXTDVBNTPTimeStartup.timeout.get().append(self.CheckXTDVBNTPTimeStartup)
        self.TimerXTDVBNTPTimeStartup.start(3000, True)

    def CheckXTDVBNTPTimeStartup(self):
        global dvbdateresult
        dvbdateresult = ''
        self.TimerXTDVBNTPTimeStartup.stop()
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.finished)
        self.container.dataAvail.append(self.dataAvail)
        self.container.execute('dvbdate --print')

    def finished(self, retval):
        self.session.open(MessageBox, _('DVB Time check results:\n%s') % dvbdateresult, MessageBox.TYPE_INFO, timeout=10)

    def dataAvail(self, str):
        global dvbdateresult
        dvbdateresult = str


class ChangeTimeWizzard(Screen):

    def __init__(self, session):
        self.session = session
        self.oldtime = strftime('%Y:%m:%d %H:%M', localtime())
        self.session.openWithCallback(self.askForNewTime, InputBox, windowTitle=_('Please Enter new Systemtime:'), title=_('OK will set new time and restart Enigma 2 !'), text='%s' % self.oldtime, maxSize=16, type=Input.NUMBER)

    def askForNewTime(self, newclock):
        try:
            length = len(newclock)
        except:
            length = 0

        if newclock is None:
            self.skipChangeTime(_('No new time input !'))
        elif (length == 16) is False:
            self.skipChangeTime(_('New time string too short !'))
        elif (newclock.count(' ') < 1) is True:
            self.skipChangeTime(_('Invalid format !'))
        elif (newclock.count(':') < 3) is True:
            self.skipChangeTime(_('Invalid format !'))
        else:
            full = []
            full = newclock.split(' ', 1)
            newdate = full[0]
            newtime = full[1]
            parts = []
            parts = newdate.split(':', 2)
            newyear = parts[0]
            newmonth = parts[1]
            newday = parts[2]
            parts = newtime.split(':', 1)
            newhour = parts[0]
            newmin = parts[1]
            maxmonth = 31
            if int(newmonth) == 4 or int(newmonth) == 6 or int(newmonth) == 9 or (int(newmonth) == 11) is True:
                maxmonth = 30
            elif (int(newmonth) == 2) is True:
                if (4 * int(int(newyear) / 4) == int(newyear)) is True:
                    maxmonth = 28
                else:
                    maxmonth = 27
            if int(newyear) < 2010 or int(newyear) > 2015 or (len(newyear) < 4) is True:
                self.skipChangeTime(_('Invalid year %s !') % newyear)
            elif int(newmonth) < 0 or int(newmonth) > 12 or (len(newmonth) < 2) is True:
                self.skipChangeTime(_('Invalid month %s !') % newmonth)
            elif int(newday) < 1 or int(newday) > maxmonth or (len(newday) < 2) is True:
                self.skipChangeTime(_('Invalid day %s !') % newday)
            elif int(newhour) < 0 or int(newhour) > 23 or (len(newhour) < 2) is True:
                self.skipChangeTime(_('Invalid hour %s !') % newhour)
            elif int(newmin) < 0 or int(newmin) > 59 or (len(newmin) < 2) is True:
                self.skipChangeTime(_('Invalid minute %s !') % newmin)
            else:
                self.newtime = '%s%s%s%s%s' % (newyear,
                 newmonth,
                 newday,
                 newhour,
                 newmin)
                self.session.openWithCallback(self.DoChangeTimeRestart, MessageBox, _('Enigma 2 must be restarted to set the new Systemtime ?'), MessageBox.TYPE_YESNO)

    def DoChangeTimeRestart(self, answer):
        if answer is None:
            self.skipChangeTime(_('Answer is none'))
        if answer is False:
            self.skipChangeTime(_('Enigma 2 restart abort by user !'))
        else:
            system('date %s' % self.newtime)
            quitMainloop(3)

    def skipChangeTime(self, reason):
        self.session.open(MessageBox, _('Change Systemtime was canceled:\n\n%s') % reason, MessageBox.TYPE_ERROR)
        

def DVBNTPautostart(reason, **kwargs):
    global session
    if config.plugins.dvbntptime.tdtautocheck.value:
        if reason == 0 and kwargs.has_key('session'):
            session = kwargs['session']
            print '[XTPanel] Using DVB Transponder Time.'
            session.open(XTDVBNTPTimeStartup)
    if config.plugins.dvbntptime.ntpautocheck.value:
        if reason == 0 and kwargs.has_key('session'):
            session = kwargs['session']
            print '[XTPanel] Using NTP-Server as Source for Enigma2 Timebase sync.'
            session.open(NTPStartup)
            
def find_in_list(list, search, listpos = 0):
    print 'searching for %s in : ' % search
    print list
    index = -1
    for item in list:
        index = index + 1
        print 'searching for %s item == %s : ' % (search, item[listpos])
        if item[listpos] == search:
            print 'find_in_list returned: %d' % index
            return index

    print 'find_in_list returned nothing'
    return -1


def write_cache(cache_file, cache_data):
    if not os_path.isdir(os_path.dirname(cache_file)):
        try:
            mkdir(os_path.dirname(cache_file))
        except OSError:
            print os_path.dirname(cache_file), 'is a file'

    fd = open(cache_file, 'w')
    dump(cache_data, fd, -1)
    fd.close()


def valid_cache(cache_file, cache_ttl):
    try:
        mtime = stat(cache_file)[ST_MTIME]
    except:
        return 0

    curr_time = time()
    if curr_time - mtime > cache_ttl:
        return 0
    else:
        return 1


def load_cache(cache_file):
    fd = open(cache_file)
    cache_data = load(fd)
    fd.close()
    return cache_data


def find_in_list(list, search, listpos = 0):
    for item in list:
        if item[listpos] == search:
            return True

    return False


global_session = None
