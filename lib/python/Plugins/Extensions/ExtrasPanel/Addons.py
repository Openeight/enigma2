from enigma import *
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.GUIComponent import GUIComponent
from Components.HTMLComponent import HTMLComponent
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from Components.Label import Label
from Components.ProgressBar import ProgressBar
from Tools.Directories import fileExists
from Components.Pixmap import Pixmap
from Components.FileList import FileList
from Components.config import config
from Extra.ExtrasList import ExtrasList, SimpleEntry
from Extra.ExtraMessageBox import ExtraMessageBox
from Extra.ExtraActionBox import ExtraActionBox
import re
import os
from __init__ import _
from Components.Ipkg import IpkgComponent
from Screens.Ipkg import Ipkg

class AddonsFileBrowser(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self['filelist'] = FileList('/tmp', matchingPattern='(?i)^.*\\.(ipk|tar\\.gz|tgz|tar.bz2|zip|rar)')
        self['FilelistActions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.ok,
         'red': self.ok,
         'cancel': self.exit,
         'blue': self.exit})
        self['key_green'] = Button('')
        self['key_red'] = Button(_('OK'))
        self['key_blue'] = Button(_('Exit'))
        self['key_yellow'] = Button('')
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        self.setTitle('%s - %s' % (_('Manual Addon Installer - Filebrowser'), '/tmp'))

    def tgz(self):
        self.tgzret = os.system('tar -xzpvf "%s" -C /' % self.filename)

    def unzip(self):
        self.unzipret = os.system('unzip -o -d / "%s"' % self.filename)

    def unrar(self):
        self.unrarret = os.system('unrar x -u "%s" /' % self.filename)

    def ok(self):
        if self['filelist'].canDescent():
            self['filelist'].descent()
            self.setTitle('%s - %s' % (_('Manual Addon Installer - Filebrowser'), self['filelist'].getCurrentDirectory()))
        else:
            filename = self['filelist'].getCurrentDirectory() + '/' + self['filelist'].getFilename()
            if filename[-3:] == 'ipk':
                self.oktext = _('\nAfter pressing OK, please wait!')
                self.cmdList = []
                self.cmdList.append((IpkgComponent.CMD_INSTALL, {'package': filename}))
                if len(self.cmdList):
                    self.session.openWithCallback(self.runUpgrade, MessageBox, _('Do you want to install the package:\n') + filename + '\n' + self.oktext)
            elif filename[-6:] == 'tar.gz' or filename[-3:] == 'tgz' or filename[-7:] == 'tar.bz2':
                self.oktext = _('\nAfter pressing OK, please wait!')
                self.filename = filename
                self.session.openWithCallback(self.runUpgrade2, MessageBox, _('Do you want to install the package:\n') + filename + '\n' + self.oktext)
            elif filename[-3:] == 'rar':
                self.oktext = _('\nAfter pressing OK, please wait!')
                self.filename = filename
                self.session.openWithCallback(self.runUpgrade3, MessageBox, _('Do you want to install the package:\n') + filename + '\n' + self.oktext)
            elif filename[-3:] == 'zip':
                self.oktext = _('\nAfter pressing OK, please wait!')
                self.filename = filename
                self.session.openWithCallback(self.runUpgrade4, MessageBox, _('Do you want to install the package:\n') + filename + '\n' + self.oktext)

    def tgzexit(self, result):
        if self.tgzret == 0:
            self.session.open(MessageBox, _('Package installed succesfully'), MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, _('Error installing package'), MessageBox.TYPE_ERROR)

    def unzipexit(self, result):
        if self.unzipret == 0:
            self.session.open(MessageBox, _('Package installed succesfully'), MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, _('Error installing package'), MessageBox.TYPE_ERROR)

    def unrarexit(self, result):
        if self.unrarret == 0:
            self.session.open(MessageBox, _('Package installed succesfully'), MessageBox.TYPE_INFO)
        else:
            self.session.open(MessageBox, _('Error installing package'), MessageBox.TYPE_ERROR)

    def exit(self):
        self.close()

    def runUpgrade(self, result):
        if result:
            self.session.openWithCallback(self.runUpgradeFinished, Ipkg, cmdList=self.cmdList)

    def runUpgrade2(self, result):
        if result:
            self.session.openWithCallback(self.tgzexit, ExtraActionBox, _('Deflating %s to /') % self['filelist'].getFilename(), _('Addons install tar.gz or tgz or tar.bz2'), self.tgz)

    def runUpgrade3(self, result):
        if result:
            self.session.openWithCallback(self.unrarexit, ExtraActionBox, _('Deflating %s to /') % self['filelist'].getFilename(), _('Addons install rar'), self.unrar)

    def runUpgrade4(self, result):
        if result:
            self.session.openWithCallback(self.unzipexit, ExtraActionBox, _('Deflating %s to /') % self['filelist'].getFilename(), _('Addons install zip'), self.unzip)

    def runUpgradeFinished(self):
        self.session.openWithCallback(self.UpgradeReboot, MessageBox, _('Installation/Upgrade finished.') + ' ' + _('Do you want to restart Enigma2?'), MessageBox.TYPE_YESNO)

    def UpgradeReboot(self, result):
        if result is None or False:
            return
        if result:
            quitMainloop(3)
