# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/fstabViewer.py
from . import _
from Components.config import config, ConfigText, ConfigNumber, ConfigSelection, NoSave, getConfigListEntry, ConfigInteger
from Components.ActionMap import *
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.MenuList import MenuList
from Components.Sources.Boolean import Boolean
from Components.MultiContent import MultiContentEntryText
from Components.Pixmap import Pixmap
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Tools.Directories import fileExists
from dirSelect import dirSelectDlg
from enigma import RT_HALIGN_LEFT, RT_HALIGN_RIGHT, eListboxPythonMultiContent, gFont
import os
import skin
entryList = []
lengthList = [0,
 0,
 0,
 0]

class fstabMenuList(MenuList):

    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        try:
            font = skin.fonts.get('fstabMenuList', ('Regular', 20, 220))
            self.l.setFont(0, gFont(font[0], font[1]))
            self.l.setItemHeight(font[2])
        except:
            self.l.setFont(0, gFont('Regular', 20))
            self.l.setItemHeight(220)


def fstabMenuListEntry(devicename, mountpoint, fstype, options, dumpfreq, passnum):
    res = [(devicename,
      mountpoint,
      fstype,
      options,
      dumpfreq,
      passnum)]
    try:
        x, y, w, h, x1, y1, w1, h1 = skin.parameters.get('fstabMenuList', (0, 0, 200, 25, 230, 0, 370, 25))
    except:
        x = 0
        y = 0
        w = 200
        h = 25
        x1 = 230
        y1 = 0
        w1 = 370
        h1 = 25

    res.append(MultiContentEntryText(pos=(x, 30 + y), size=(w, h), font=0, flags=RT_HALIGN_RIGHT, text=_('Device name:')))
    res.append(MultiContentEntryText(pos=(x, 60 + y), size=(w, h), font=0, flags=RT_HALIGN_RIGHT, text=_('Mount point:')))
    res.append(MultiContentEntryText(pos=(x, 90 + y), size=(w, h), font=0, flags=RT_HALIGN_RIGHT, text=_('File system type:')))
    res.append(MultiContentEntryText(pos=(x, 120 + y), size=(w, h), font=0, flags=RT_HALIGN_RIGHT, text=_('Options:')))
    res.append(MultiContentEntryText(pos=(x, 150 + y), size=(w, h), font=0, flags=RT_HALIGN_RIGHT, text=_('Dump frequency:')))
    res.append(MultiContentEntryText(pos=(x, 180 + y), size=(w, h), font=0, flags=RT_HALIGN_RIGHT, text=_('Pass number:')))
    res.append(MultiContentEntryText(pos=(x1, 30 + y1), size=(w1, h1), font=0, text=devicename))
    res.append(MultiContentEntryText(pos=(x1, 60 + y1), size=(w1, h1), font=0, text=mountpoint))
    res.append(MultiContentEntryText(pos=(x1, 90 + y1), size=(w1, h1), font=0, text=fstype))
    res.append(MultiContentEntryText(pos=(x1, 120 + y1), size=(w1, h1), font=0, text=options))
    res.append(MultiContentEntryText(pos=(x1, 150 + y1), size=(w1, h1), font=0, text=dumpfreq))
    res.append(MultiContentEntryText(pos=(x1, 180 + y1), size=(w1, h1), font=0, text=passnum))
    return res


class fstabViewerScreen(Screen, HelpableScreen):
    skin = '\n\t\t<screen position="center,center" size="600,430" title="fstab-Editor" >\n\t\t\t<widget name="entryinfo" position="0,10" size="580,20" halign="right" font="Regular;17" transparent="1" />\n\t\t\t<widget name="menulist" position="0,40" size="600,220" scrollbarMode="showNever" />\n\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/fstabEditor.png" position="70,304" size="100,40"/>\n\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/ok.png" position="230,300" size="35,25"/>\n\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/exit.png" position="230,325" size="35,25"/>\n\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/green.png" position="230,350" size="35,25"/>\n\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/blue.png" position="230,375" size="35,25"/>\n\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/yellow.png" position="230,400" size="35,25"/>\n\t\t\t<widget name="edit" font="Regular;18" position="270,303" size="200,25" transparent="1"/>\n\t\t\t<widget name="cancelist" font="Regular;18" position="270,328" size="225,20" transparent="1"/>\n\t\t\t<widget name="addentry" font="Regular;18" position="270,353" size="225,20" transparent="1"/>\n\t\t\t<widget name="run" font="Regular;18" position="270,378" size="225,20" transparent="1"/>\n\t\t\t<widget name="restore" font="Regular;18" position="270,403" size="320,20" transparent="1"/>\n\t\t</screen>'

    def __init__(self, session, args = 0):
        self.skin = fstabViewerScreen.skin
        self.session = session
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self['entryinfo'] = Label()
        self['edit'] = Label(_('Edit'))
        self['cancelist'] = Label(_('Cancel'))
        self['addentry'] = Label(_('Add entry'))
        self['run'] = Label(_('Run mount -a'))
        self['restore'] = Label('')
        self['menulist'] = fstabMenuList([])
        self.fstabEntryList = []
        self['ColorActions'] = HelpableActionMap(self, 'ColorActions', {'green': (self.addEntry, _('Add entry')),
         'yellow': (self.restoreBackUp, _('Restore backup fstab')),
         'blue': (self.mountall, _('Run mount -a')),
         'red': (self.close, _('Close plugin'))}, -1)
        self['OkCancelActions'] = HelpableActionMap(self, 'OkCancelActions', {'cancel': (self.close, _('Close plugin')),
         'ok': (self.openEditScreen, _('Open editor'))}, -1)
        self.setTitle(_('fstab-Editor'))
        self.builderror = False
        if fileExists('/etc/fstab'):
            self.buildScreen()
        if fileExists('/etc/fstab.backup') or fileExists('/etc/fstab-opkg'):
            self['restore'].setText(_('Restore fstab'))
        self['menulist'].onSelectionChanged.append(self.selectionChanged)

    def openEditScreen(self):
        global entryList
        if not self.builderror:
            self.selectedEntry = self['menulist'].getSelectedIndex()
            if not self.checkSoftwareEntry(entryList[self.selectedEntry][0]):
                self.session.openWithCallback(self.writeFile, fstabEditorScreen, selectedEntry=self.selectedEntry)
            else:
                self.session.openWithCallback(self.openEditSystemEntryScreen, MessageBox, _('Attention!\nNot highly recommend that you remove or edit the system entry!\n') + _('Really edit the selected entry?'), MessageBox.TYPE_YESNO)

    def openEditSystemEntryScreen(self, answer):
        if answer:
            self.selectedEntry = self['menulist'].getSelectedIndex()
            self.session.openWithCallback(self.writeFile, fstabEditorScreen, selectedEntry=self.selectedEntry)

    def buildScreen(self):
        global entryList
        self.fstabEntryList = []
        entryList = []
        lengthList = [0,
         0,
         0,
         0]
        if fileExists('/etc/fstab'):
            fstabFile = open('/etc/fstab', 'r')
            self.counter = 0
            for line in fstabFile:
                if line[0] != '\n' and line[0] != '#':
                    try:
                        entry = line.split()
                        if entry in entryList:
                            continue
                        entryList.append(entry)
                        if len(entry[0]) > lengthList[0]:
                            lengthList[0] = len(entry[0])
                        if len(entry[1]) > lengthList[1]:
                            lengthList[1] = len(entry[1])
                        if len(entry[2]) > lengthList[2]:
                            lengthList[2] = len(entry[2])
                        if len(entry[3]) > lengthList[3]:
                            lengthList[3] = len(entry[3])
                        self.fstabEntryList.append(fstabMenuListEntry(entry[0], entry[1], entry[2], entry[3], entry[4], entry[5]))
                        self.counter = self.counter + 1
                    except:
                        fstabFile.close()
                        self.fstabEntryList = []
                        self['menulist'].l.setList(self.fstabEntryList)
                        self['entryinfo'].setText(_('Failed to read /etc/fstab! Restore fstab.backup or edit the file manually.'))
                        fstabFile.close()
                        self.builderror = True
                        return -1

            fstabFile.close()
        self['menulist'].l.setList(self.fstabEntryList)
        self['entryinfo'].setText('%d / %d' % (self['menulist'].getSelectedIndex() + 1, self.counter))

    def writeFile(self, returnvalue):
        global lengthList
        if returnvalue != 0 and not self.builderror:
            os.system('cp /etc/fstab /etc/fstab.backup')
            configFile = open('/etc/fstab', 'w')
            for i in range(len(entryList)):
                try:
                    line = '%*s %*s %*s %*s %s %s\n' % (int(lengthList[0]) * -1,
                     entryList[i][0],
                     int(lengthList[1]) * -1,
                     entryList[i][1],
                     int(lengthList[2]) * -1,
                     entryList[i][2],
                     int(lengthList[3]) * -1,
                     entryList[i][3],
                     str(entryList[i][4]),
                     str(entryList[i][5]))
                    configFile.write(line)
                except:
                    configFile.close()
                    return -1

            configFile.close()
            self.buildScreen()

    def selectionChanged(self):
        if not self.builderror:
            self['entryinfo'].setText('%d / %d' % (self['menulist'].getSelectedIndex() + 1, self.counter))

    def mountall(self):
        if not self.builderror:
            os.system('mount -a')

    def checkSoftwareEntry(self, entry = ''):
        if entry and ('proc' in entry or 'tmpfs' in entry or 'jffs2' in entry or 'usbfs' in entry or 'usbdevfs' in entry or 'devpts' in entry or 'rootfs' in entry):
            return True
        return False

    def addEntry(self):
        if not self.builderror:
            menu = [(_('Add new entry'), 'new')]
            selectedEntry = self['menulist'].getSelectedIndex()
            if selectedEntry and not self.checkSoftwareEntry(entryList[selectedEntry][0]):
                menu.append((_('Clone selected entry'), 'clone'))
            if len(menu) == 1:
                self.addNewEntry()
            elif len(menu) == 2:

                def setAction(choice):
                    if choice is not None:
                        if choice[1] == 'new':
                            self.addNewEntry()
                        elif choice[1] == 'clone':
                            self.cloneEntry()
                    return

                self.session.openWithCallback(setAction, ChoiceBox, title=_('Select action:'), list=menu)

    def cloneEntry(self):
        if not self.builderror:
            selectedEntry = self['menulist'].getSelectedIndex()
            self.session.openWithCallback(self.writeFile, fstabEditorScreen, selectedEntry=selectedEntry, cloneEntry=True)

    def addNewEntry(self):
        if not self.builderror:
            self.session.openWithCallback(self.writeFile, fstabEditorScreen, selectedEntry=None, addEntry=True)
        return

    def restoreBackUp(self):
        list = []
        backup = fileExists('/etc/fstab.backup')
        if backup:
            list.append((_('Restore fstab.backup'), 'backup'))
        default = fileExists('/etc/fstab-opkg')
        if default:
            list.append((_('Restore default fstab'), 'default'))
        if len(list) > 1:

            def setAction(choice):
                if choice is not None:
                    if choice[1] == 'backup':
                        os.system('rm -f /etc/fstab')
                        os.system('cp /etc/fstab.backup /etc/fstab')
                    elif choice[1] == 'default':
                        os.system('rm -f /etc/fstab')
                        os.system('cp /etc/fstab-opkg /etc/fstab')
                    self.session.open(MessageBox, _('fstab restored!'), MessageBox.TYPE_INFO, timeout=5)
                    self.builderror = False
                    self.buildScreen()
                return

            self.session.openWithCallback(setAction, ChoiceBox, title=_('Select action:'), list=list)
        else:
            self.session.open(MessageBox, _('Not found restore file!'), MessageBox.TYPE_ERROR, timeout=5)


class fstabEditorScreen(Screen, ConfigListScreen, HelpableScreen):
    skin = '\n\t\t<screen position="center,center" size="600,380" title="fstab-Editor" >\n\t\t\t<widget itemHeight="28" name="config" position="0,40" size="600,224" scrollbarMode="showOnDemand"/>\n\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/fstabEditor.png" position="70,275" size="100,40"/>\n\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/green.png" position="230,300" size="35,25"/>\n\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/exit.png" position="230,325" size="35,25"/>\n\t\t\t<widget name="ButtonBlue" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/blue.png" position="230,350" zPosition="10" size="35,25" transparent="1" alphatest="on" />\n\t\t\t<widget name="save" font="Regular;18" position="270,303" size="200,25" transparent="1"/>\n\t\t\t<widget name="cansel" font="Regular;18" position="270,328" size="200,25" transparent="1"/>\n\t\t\t<widget name="ButtonBlueText" position="270,353" size="200,25" zPosition="10" font="Regular;18" foregroundColor="#f0f0f0" transparent="1" />\n\t\t\t<widget source="VKeyIcon" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/key_text.png" position="10,304" zPosition="10" size="35,25" transparent="1" alphatest="on" >\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t</widget>\n\t\t\t<widget name="ButtonOK" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/ok.png" zPosition="10" position="230,275" size="35,25" transparent="1" alphatest="on"/>\n\t\t\t<widget name="HelpWindow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/vkey_icon.png" position="10,350" zPosition="10" size="60,48" transparent="1" alphatest="on" />\n\t\t</screen>'

    def __init__(self, session, selectedEntry = None, addEntry = False, cloneEntry = False):
        self.skin = fstabEditorScreen.skin
        self.session = session
        self.selectedEntry = selectedEntry
        self.addEntry = addEntry
        self.cloneEntry = cloneEntry
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self['ButtonBlue'] = Pixmap()
        self['ButtonOK'] = Pixmap()
        self['ButtonBlueText'] = Label(_('Remove entry'))
        self['save'] = Label(_('Save'))
        self['cansel'] = Label(_('Cancel'))
        if self.addEntry or self.cloneEntry:
            self['ButtonBlue'].hide()
            self['ButtonBlueText'].hide()
        if self.cloneEntry:
            self['ButtonOK'].hide()
        else:
            self['ButtonOK'].show()
        self['ColorActions'] = HelpableActionMap(self, 'ColorActions', {'green': (self.checkEntry, _('Return with saving')),
         'red': (self.cancelEntry, _('Return without saving')),
         'blue': (self.removeEntry, _('Remove entry'))}, -1)
        self['OkCancelActions'] = HelpableActionMap(self, 'OkCancelActions', {'cancel': (self.cancelEntry, _('Return without saving')),
         'ok': (self.ok, _('Open selector'))}, -1)
        self.setTitle(_('fstab-Editor'))
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=self.session)
        self['VKeyIcon'] = Boolean(False)
        self['HelpWindow'] = Pixmap()
        self['HelpWindow'].hide()
        if self.addEntry:
            self.devicename = NoSave(ConfigText(default='', fixed_size=False))
            self.mountpoint = NoSave(ConfigText(default='', fixed_size=False))
            self.fstype = NoSave(ConfigSelection([('auto', 'auto'),
             ('ext2', 'ext2'),
             ('ext3', 'ext3'),
             ('ext4', 'ext4'),
             ('cifs', 'cifs'),
             ('nfs', 'nfs'),
             ('swap', 'swap'),
             ('proc', 'proc'),
             ('tmpfs', 'tmpfs'),
             ('jffs2', 'jffs2'),
             ('rootfs', 'rootfs'),
             ('usbfs', 'usbfs'),
             ('usbdevfs', 'usbdevfs'),
             ('devpts', 'devpts'),
             ('reiserfs', 'reiserfs'),
             ('btrfs', 'btrfs'),
             ('ntfs-3g', 'ntfs-3g'),
             ('vfat', 'vfat'),
             ('fat', 'fat'),
             ('ntfs', 'ntfs'),
             ('xfs', 'xfs')], default='auto'))
            self.options = NoSave(ConfigText(default='defaults', fixed_size=False))
            self.dumpfreq = NoSave(ConfigInteger(limits=(0, 1), default=0))
            self.passnum = NoSave(ConfigSelection([('0', '0'), ('1', '1'), ('2', '2')], default='0'))
        else:
            self.devicename = NoSave(ConfigText(fixed_size=False, default=entryList[self.selectedEntry][0]))
            self.mountpoint = NoSave(ConfigText(fixed_size=False, default=entryList[self.selectedEntry][1]))
            self.fstype = NoSave(ConfigSelection([('auto', 'auto'),
             ('ext2', 'ext2'),
             ('ext3', 'ext3'),
             ('ext4', 'ext4'),
             ('cifs', 'cifs'),
             ('nfs', 'nfs'),
             ('swap', 'swap'),
             ('proc', 'proc'),
             ('tmpfs', 'tmpfs'),
             ('jffs2', 'jffs2'),
             ('rootfs', 'rootfs'),
             ('usbfs', 'usbfs'),
             ('usbdevfs', 'usbdevfs'),
             ('devpts', 'devpts'),
             ('reiserfs', 'reiserfs'),
             ('btrfs', 'btrfs'),
             ('ntfs-3g', 'ntfs-3g'),
             ('vfat', 'vfat'),
             ('fat', 'fat'),
             ('ntfs', 'ntfs'),
             ('xfs', 'xfs')], default=entryList[self.selectedEntry][2]))
            self.options = NoSave(ConfigText(fixed_size=False, default=entryList[self.selectedEntry][3]))
            self.dumpfreq = NoSave(ConfigInteger(limits=(0, 1), default=int(entryList[self.selectedEntry][4])))
            self.passnum = NoSave(ConfigSelection([('0', '0'), ('1', '1'), ('2', '2')], default=entryList[self.selectedEntry][5]))
        self.list.append(getConfigListEntry(_('device name: '), self.devicename))
        self.list.append(getConfigListEntry(_('mount point: '), self.mountpoint))
        self.list.append(getConfigListEntry(_('file system type (auto): '), self.fstype))
        self.list.append(getConfigListEntry(_('options mount file system (default): '), self.options))
        self.list.append(getConfigListEntry(_('dump (0 - create backup off): '), self.dumpfreq))
        self.list.append(getConfigListEntry(_('pass num (0 - fsck off): '), self.passnum))
        self['config'].setList(self.list)
        self['config'].onSelectionChanged.append(self.selectionChanged)

    def selectionChanged(self):
        if self.cloneEntry:
            self['ButtonOK'].hide()
            return
        if self.getCurrentEntry() == _('device name: ') or self.getCurrentEntry() == _('mount point: '):
            self['ButtonOK'].show()
        else:
            self['ButtonOK'].hide()

    def checkEntry(self):
        if self.devicename.value == '' or self.mountpoint.value == '' or self.options.value == '':
            error = self.session.open(MessageBox, _('Please enter a value for every input field!'), MessageBox.TYPE_ERROR, timeout=6)
        else:
            self.saveEntry()

    def checkSoftwareEntry(self):
        entry = self.devicename.value
        if entry and ('proc' in entry or 'tmpfs' in entry or 'jffs2' in entry or 'usbfs' in entry or 'usbdevfs' in entry or 'devpts' in entry or 'rootfs' in entry):
            return _('Attention!\nNot highly recommend that you remove or edit the system entry!\n')
        return ''

    def saveEntry(self):
        if self.devicename.value == '' or self.mountpoint.value == '' or self.options.value == '':
            self.session.open(MessageBox, _('Please enter a value for every input field!'), MessageBox.TYPE_ERROR, timeout=6)
            return
        if self.passnum.value == '1' and self.mountpoint.value != '/':
            self.session.open(MessageBox, _("Pass num value 1 use only for root filesystem (mountpoint '/')!"), MessageBox.TYPE_ERROR, timeout=6)
            return
        new_entry = [self.devicename.value,
         self.mountpoint.value,
         self.fstype.value,
         self.options.value,
         str(self.dumpfreq.value),
         self.passnum.value]
        if new_entry in entryList:
            self.session.open(MessageBox, _('This entry already exists in the fstab!'), MessageBox.TYPE_ERROR, timeout=6)
            return
        if len(self.devicename.value) > lengthList[0]:
            lengthList[0] = len(self.devicename.value)
        if len(self.mountpoint.value) > lengthList[1]:
            lengthList[1] = len(self.mountpoint.value)
        if len(self.fstype.value) > lengthList[2]:
            lengthList[2] = len(self.fstype.value)
        if len(self.options.value) > lengthList[3]:
            lengthList[3] = len(self.options.value)
        if self.addEntry or self.cloneEntry:
            entryList.append(new_entry)
        else:
            entryList[self.selectedEntry] = new_entry
        try:
            if not os.path.exists(self.mountpoint.value):
                os.mkdir(self.mountpoint.value, 493)
        except:
            pass

        self.close(1)

    def removeEntry(self):
        if not self.addEntry and not self.cloneEntry:
            self.session.openWithCallback(self.removeEntryAnswer, MessageBox, self.checkSoftwareEntry() + _('Really delete the selected entry?'), MessageBox.TYPE_YESNO)

    def removeEntryAnswer(self, answer):
        if answer:
            del entryList[self.selectedEntry]
            self.close(1)

    def cancelEntry(self):
        self.close(0)

    def ok(self):
        if not self.cloneEntry:
            self.selectedEntry = self['config'].getCurrentIndex()
            if self.selectedEntry is not None:
                self.session.openWithCallback(self.dirSelectDlgClosed, dirSelectDlg, '/media/dummy/', False)
            else:
                self.session.openWithCallback(self.dirSelectDlgClosed, dirSelectDlg, '/dev/dummy/', True)
        return

    def dirSelectDlgClosed(self, mountpoint):
        if mountpoint != False:
            if self.selectedEntry is not None:
                self.mountpoint.value = mountpoint
            else:
                self.devicename.value = mountpoint
        return
