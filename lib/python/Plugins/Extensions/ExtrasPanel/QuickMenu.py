from enigma import eListboxPythonMultiContent, gFont, eEnv, getDesktop, getBoxType
from boxbranding import getMachineBrand, getMachineName
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.Network import iNetwork
from Components.NimManager import nimmanager
from Components.SystemInfo import SystemInfo
from Screens.Screen import Screen
from Screens.NetworkSetup import *
from Screens.About import About
from Screens.PluginBrowser import PluginDownloadBrowser, PluginFilter, PluginBrowser
from Screens.LanguageSelection import LanguageSelection
from Screens.Satconfig import NimSelection
from Screens.ScanSetup import ScanSimple, ScanSetup
from Screens.Setup import Setup, getSetupTitle
from Screens.HarddiskSetup import HarddiskSelection, HarddiskFsckSelection
from Screens.Ipkuninstall import Ipkuninstall
from Screens.SetupFallbacktuner import SetupFallbacktuner
from Screens.SkinSelector import SkinSelector, LcdSkinSelector
from Screens.RecordPaths import RecordPathsSettings
from Screens.CCcamInfo import CCcamInfoMain
from Screens.OScamInfo import OscamInfoMenu
from Screens.FlashImage import SelectImage
from Screens.Hotkey import HotkeySetup
from Plugins.SystemPlugins.Videomode.plugin import videoSetupMain
from Plugins.Plugin import PluginDescriptor
from Plugins.SystemPlugins.Satfinder.plugin import Satfinder
from Plugins.SystemPlugins.NetworkBrowser.MountManager import AutoMountManager
from Plugins.SystemPlugins.NetworkBrowser.NetworkBrowser import NetworkBrowser
from Plugins.SystemPlugins.NetworkBrowser.AutoMount import AutoMount
from Plugins.SystemPlugins.NetworkWizard.NetworkWizard import NetworkWizard
from Plugins.Extensions.AutoBackup.ui import Config, BackupSelection
from Plugins.Extensions.ExtrasPanel.RestartNetwork import RestartNetwork
from Plugins.Extensions.ExtrasPanel.plugin import Extraspanel
from Plugins.Extensions.ExtrasPanel.MountManager import DevicesMountPanel
from Plugins.Extensions.ExtrasPanel.SoftcamPanel import *
from Plugins.Extensions.ExtrasPanel.plugin import ShowSoftcamPanelExtensions
from Plugins.Extensions.ExtrasPanel.SoftwarePanel import SoftwarePanel
from Plugins.Extensions.ExtrasPanel.sundtek import SundtekControlCenter
from Addons import AddonsFileBrowser
from Plugins.SystemPlugins.SoftwareManager.ImageBackup import ImageBackup
from Plugins.SystemPlugins.SoftwareManager.plugin import UpdatePlugin, SoftwareManagerSetup
from Plugins.SystemPlugins.SoftwareManager.BackupRestore import BackupScreen, RestoreScreen, BackupSelection, getBackupPath, getOldBackupPath, getBackupFilename
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_SKIN
from Tools.LoadPixmap import LoadPixmap
from os import path, listdir
from time import sleep
from re import search
import NavigationInstance
import os.path
import fstabViewer
plugin_path_networkbrowser = eEnv.resolve('${libdir}/enigma2/python/Plugins/SystemPlugins/NetworkBrowser')
if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/HdmiCEC/plugin.pyo'):
	from Plugins.SystemPlugins.HdmiCEC.plugin import HdmiCECSetupScreen
	HDMICEC = True
else:
	HDMICEC = False
if path.exists('/usr/lib/enigma2/python/Plugins/Extensions/AudioSync'):
	from Plugins.Extensions.AudioSync.AC3setup import AC3LipSyncSetup
	plugin_path_audiosync = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/AudioSync')
	AUDIOSYNC = True
else:
	AUDIOSYNC = False
if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AutomaticVolumeAdjustment'):
	from Plugins.SystemPlugins.AutomaticVolumeAdjustment.AutomaticVolumeAdjustmentSetup import AutomaticVolumeAdjustmentConfigScreen
	AUTVOLADJ = True
else:
	AUTVOLADJ = False
if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/VideoTune/VideoFinetune.pyo'):
	from Plugins.SystemPlugins.VideoTune.VideoFinetune import VideoFinetune
	VIDTUNE = True
else:
	VIDTUNE = False
if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/VideoEnhancement/plugin.pyo'):
	from Plugins.SystemPlugins.VideoEnhancement.plugin import VideoEnhancementSetup
	VIDEOENH = True
else:
	VIDEOENH = False
if path.exists('/usr/lib/enigma2/python/Plugins/Extensions/dFlash'):
	from Plugins.Extensions.dFlash.plugin import dFlash
	DFLASH = True
else:
	DFLASH = False
if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/PositionerSetup/plugin.pyo'):
	from Plugins.SystemPlugins.PositionerSetup.plugin import PositionerSetup, RotorNimSelection
	POSSETUP = True
else:
	POSSETUP = False
if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/FastScan/plugin.pyo'):
	from Plugins.SystemPlugins.FastScan.plugin import FastScanMain
	FASTSCAN = True
else:
	FASTSCAN = False
if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/Blindscan/plugin.pyo'):
	from Plugins.SystemPlugins.Blindscan.plugin import BlindscanMain
	BLINDSCAN = True
else:
	BLINDSCAN = False
if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/CableScan/plugin.pyo'):
	from Plugins.SystemPlugins.CableScan.plugin import CableScanMain
	CABLESCAN = True
else:
	CABLESCAN = False
if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/MisPlsLcnScan/plugin.pyo'):
	from Plugins.SystemPlugins.MisPlsLcnScan.plugin import MisPlsLcnScanMain
	MISPLSLCNSCAN = True
else:
	MISPLSLCNSCAN = False
if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/TerrestrialScan/plugin.pyo'):
	from Plugins.SystemPlugins.TerrestrialScan.plugin import TerrestrialScanMain
	TERRESTSCAN = True
else:
	TERRESTSCAN = False
if path.exists('/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/Sc.pyo'):
	from Plugins.PLi.SoftcamSetup.Sc import ScNewSelection, ScSetupScreen
	SC = True
else:
	SC = False
if path.exists('/usr/lib/enigma2/python/Screens/SoftcamSetup.pyo'):
	from Screens.SoftcamSetup import SoftcamSetup
	SSC = True
else:
	SSC = False
if path.exists('/usr/lib/enigma2/python/Plugins/Extensions/CCcamInfo/plugin.pyo'):
	from Plugins.Extensions.CCcamInfo.plugin import EcmInfoConfigMenu
	ECMINFOSETUP = True
else:
	ECMINFOSETUP = False
if path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/AutoResolution/plugin.pyo'):
	from Plugins.SystemPlugins.AutoResolution.plugin import autoresSetup
	AUTORES = True
else:
	AUTORES = False
if path.exists('/usr/lib/enigma2/python/Plugins/Extensions/VpnChanger/plugin.pyo'):
	from Plugins.Extensions.VpnChanger.plugin import VpnScreen
	VPNCHP = True
else:
	VPNCHP = False
if path.exists('/usr/lib/enigma2/python/Plugins/Extensions/PureVPN/plugin.pyo'):
	from Plugins.Extensions.PureVPN.plugin import PureVPNScreen
	PVPN = True
else:
	PVPN = False
if path.exists('/usr/lib/enigma2/python/Plugins/Extensions/VpnManager/plugin.pyo'):
	from Plugins.Extensions.VpnManager.plugin import VpnManagerScreen
	VPNM = True
else:
	VPNM = False


def isFileSystemSupported(filesystem):
	try:
		for fs in open('/proc/filesystems', 'r'):
			if fs.strip().endswith(filesystem):
				return True

		return False
	except Exception as ex:
		print '[Harddisk] Failed to read /proc/filesystems:', ex


def Check_Softcam():
	found = False
	for x in listdir('/etc'):
		if x.find('.emu') > -1:
			found = True
			break

	return found


def Softcam_Check():
	found = False
	for x in os.listdir('/etc/init.d'):
		if x.find('softcam.') > -1 and x != 'softcam.None':
			found = True
			break

	return found


class QuickMenu(Screen):
	skin = '\n\t\t<screen name="QuickMenu" position="center,center" size="1180,600" backgroundColor="black" flags="wfBorder">\n\t\t<widget name="list" position="21,32" size="370,420" backgroundColor="black" itemHeight="60" transparent="1" />\n\t\t<widget name="sublist" position="410,32" size="300,420" backgroundColor="black" itemHeight="60" />\n\t\t<eLabel position="400,30" size="2,420" backgroundColor="#666666" zPosition="3" />\n\t\t<widget source="session.VideoPicture" render="Pig" position="720,30" size="450,300" backgroundColor="transparent" zPosition="1" />\n\t\t<widget name="description" position="22,455" size="1150,100" zPosition="1" font="Regular;22" halign="center" valign="center" backgroundColor="black" transparent="1" />\n\t\t<widget name="key_red" position="20,571" size="300,30" zPosition="1" font="Regular;22" halign="center" foregroundColor="white" backgroundColor="black" transparent="1" />\n\t\t<widget name="key_green" position="325,571" size="300,30" zPosition="1" font="Regular;22" halign="center" foregroundColor="white" backgroundColor="black" transparent="1" />\n\t\t<widget name="key_yellow" position="630,571" size="300,30" zPosition="1" font="Regular;22" halign="center" foregroundColor="white" backgroundColor="black" transparent="1" valign="center" />\n\t\t<widget name="key_blue" position="935,571" size="234,30" zPosition="1" font="Regular;22" halign="center" foregroundColor="white" backgroundColor="black" transparent="1" />\n\t\t<eLabel name="new eLabel" position="21,567" size="300,3" zPosition="3" backgroundColor="red" />\n\t\t<eLabel name="new eLabel" position="325,567" size="300,3" zPosition="3" backgroundColor="green" />\n\t\t<eLabel name="new eLabel" position="630,567" size="300,3" zPosition="3" backgroundColor="yellow" />\n\t\t<eLabel name="new eLabel" position="935,567" size="234,3" zPosition="3" backgroundColor="blue" />\n\t\t</screen> '

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _('QuickMenu') + ' - OpenEight')
		self['key_red'] = Label(_('Exit'))
		self['key_green'] = Label(_('System Info'))
		self['key_yellow'] = Label(_('Devices'))
		self['key_blue'] = Label('Eight Panel')
		self['description'] = Label()
		self.menu = 0
		self.list = []
		self['list'] = QuickMenuList(self.list)
		self.sublist = []
		self['sublist'] = QuickMenuSubList(self.sublist)
		self.selectedList = []
		self.onChangedEntry = []
		self['list'].onSelectionChanged.append(self.selectionChanged)
		self['sublist'].onSelectionChanged.append(self.selectionSubChanged)
		self['actions'] = ActionMap(['SetupActions',
		 'WizardActions',
		 'MenuActions',
		 'MoviePlayerActions'], {'ok': self.ok,
		 'back': self.keyred,
		 'cancel': self.keyred,
		 'left': self.goLeft,
		 'right': self.goRight,
		 'up': self.goUp,
		 'down': self.goDown}, -1)
		self['ColorActions'] = HelpableActionMap(self, 'ColorActions', {'red': self.keyred,
		 'green': self.keygreen,
		 'yellow': self.keyyellow,
		 'blue': self.keyblue})

		self.MainQmenu()
		self.selectedList = self['list']
		self.selectionChanged()
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self['sublist'].selectionEnabled(0)

	def selectionChanged(self):
		if self.selectedList == self['list']:
			item = self['list'].getCurrent()
			if item:
				self['description'].setText(_(item[4]))
				self.okList()

	def selectionSubChanged(self):
		if self.selectedList == self['sublist']:
			item = self['sublist'].getCurrent()
			if item:
				self['description'].setText(_(item[3]))

	def goLeft(self):
		if self.menu != 0:
			self.menu = 0
			self.selectedList = self['list']
			self['list'].selectionEnabled(1)
			self['sublist'].selectionEnabled(0)
			self.selectionChanged()

	def goRight(self):
		if self.menu == 0:
			self.menu = 1
			self.selectedList = self['sublist']
			self['sublist'].moveToIndex(0)
			self['list'].selectionEnabled(0)
			self['sublist'].selectionEnabled(1)
			self.selectionSubChanged()

	def goUp(self):
		self.selectedList.up()

	def goDown(self):
		self.selectedList.down()

	def keyred(self):
		self.close()

	def keygreen(self):
		self.session.open(About)

	def keyyellow(self):
		self.session.open(QuickMenuDevices)

	def keyblue(self):
		self.session.open(Extraspanel)

	def MainQmenu(self):
		self.menu = 0
		self.list = []
		self.oldlist = []
		self.list.append(QuickMenuEntryComponent('Software Manager', _('Update/Backup/Restore your box'), _('Update/Backup your firmware, Backup/Restore settings.')))
		if Check_Softcam() or Softcam_Check():
			self.list.append(QuickMenuEntryComponent('Softcam', _('Start/stop/select cam'), _('Start/stop/select your cam, You need to install first a softcam.')))
		self.list.append(QuickMenuEntryComponent('System', _('System Setup'), _('Setup your System.')))
		self.list.append(QuickMenuEntryComponent('Mounts', _('Mount Setup'), _('Setup your mounts for network and storage devices.')))
		self.list.append(QuickMenuEntryComponent('Network', _('Setup your local network'), _('Setup your local network. For Wlan you need to boot with a USB-Wlan stick.')))
		self.list.append(QuickMenuEntryComponent('AV Setup', _('Setup Audio/Video'), _('Setup your Video Mode, Video Output, Audio and Language Settings.')))
		self.list.append(QuickMenuEntryComponent('Tuner Setup', _('Setup Tuner'), _('Setup your Tuner and search for channels.')))
		self.list.append(QuickMenuEntryComponent('Plugins', _('Download plugins'), _('Shows available Plugins. Here you can download and install them.')))
		self.list.append(QuickMenuEntryComponent('Harddisk', _('Harddisk Setup'), _('Setup your Harddisk(s).')))
		self['list'].l.setList(self.list)

	def Qsystem(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent('Customize', _('Setup Enigma2'), _('Customize enigma2 personal settings.')))
		self.sublist.append(QuickSubMenuEntryComponent('User interface', _('User interface Setup'), _('Setup your User interface.')))
		if SystemInfo['FrontpanelDisplay'] and SystemInfo['Display']:
			self.sublist.append(QuickSubMenuEntryComponent('Display Settings', _('Display Setup'), _('Setup your display.')))
		if os.path.exists('/usr/share/enigma2/display'):
			self.sublist.append(QuickSubMenuEntryComponent('LCD Skin Setup', _('Skin Setup'), _('Setup your LCD.')))
		self.sublist.append(QuickSubMenuEntryComponent('Skin Setup', _('Select Enigma2 Skin'), _('Setup your Skin.')))
		self.sublist.append(QuickSubMenuEntryComponent('Recording and Playback settings', _('Recording/Playback Setup'), _('Setup your recording and playback config.')))
		self.sublist.append(QuickSubMenuEntryComponent('Recording paths', _('Recording paths Setup'), _('Setup your recording paths config.')))
		self.sublist.append(QuickSubMenuEntryComponent('Hotkey', _('Hotkey Setup'), _('Adjust the functions of your remote cotrol buttons.')))
		self.sublist.append(QuickSubMenuEntryComponent('EPG settings', _('EPG Setup'), _('Setup your EPG config.')))
		self.sublist.append(QuickSubMenuEntryComponent('Language', _('Language selection'), _('Choose the language of the user interface and plugins.')))
		self['sublist'].l.setList(self.sublist)

	def Qnetwork(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent('Network Wizard', _('Configure your Network'), _('Use the Networkwizard to configure your Network. The wizard will help you to setup your network.')))
		if len(self.adapters) > 1:
			self.sublist.append(QuickSubMenuEntryComponent('Network Adapter Selection', _('Select Lan/Wlan'), _('Setup your network interface. If no Wlan stick is used, you only can select Lan.')))
		if not self.activeInterface == None:
			self.sublist.append(QuickSubMenuEntryComponent('Network Interface', _('Setup interface'), _('Setup network. Here you can setup DHCP, IP, DNS.')))
		self.sublist.append(QuickSubMenuEntryComponent('Network Restart', _('Restart network with current setup'), _('Restart network and remount connections.')))
		self.sublist.append(QuickSubMenuEntryComponent('Network Services', _('Setup Network Services'), _('Setup Network Services (Samba, Ftp, NFS, ...)')))
		if path.exists('/var/lib/opkg/info/openvpn.control'):
			self.sublist.append(QuickSubMenuEntryComponent('OpenVPN', _('Setup OpenVPN'), _('Setup OpenVPN')))
			if VPNM:
				self.sublist.append(QuickSubMenuEntryComponent('VPN Manager', _('Setup VPN Manager'), _('Setup VPN Manager for more privacy.')))
			if VPNCHP:
				self.sublist.append(QuickSubMenuEntryComponent('VPN Changer', _('Setup VPN Changer'), _('Setup VPN Changer for more privacy.')))
			if PVPN:
				self.sublist.append(QuickSubMenuEntryComponent('PureVPN Manager', _('Setup PureVPN'), _('Setup PureVPN for more privacy.')))
		self['sublist'].l.setList(self.sublist)
		return

	def Qnetworkservices(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent('Samba', _('Setup Samba'), _('Setup Samba')))
		self.sublist.append(QuickSubMenuEntryComponent('NFS', _('Setup NFS'), _('Setup NFS')))
		self.sublist.append(QuickSubMenuEntryComponent('FTP', _('Setup FTP'), _('Setup FTP')))
		self.sublist.append(QuickSubMenuEntryComponent('AFP', _('Setup AFP'), _('Setup AFP')))
		self.sublist.append(QuickSubMenuEntryComponent('OpenVPN', _('Setup OpenVPN'), _('Setup OpenVPN')))
		self.sublist.append(QuickSubMenuEntryComponent('MiniDLNA', _('Setup MiniDLNA'), _('Setup MiniDLNA')))
		self.sublist.append(QuickSubMenuEntryComponent('Inadyn', _('Setup Inadyn'), _('Setup Inadyn')))
		self.sublist.append(QuickSubMenuEntryComponent('SABnzbd', _('Setup SABnzbd'), _('Setup SABnzbd')))
		self.sublist.append(QuickSubMenuEntryComponent('uShare', _('Setup uShare'), _('Setup uShare')))
		self.sublist.append(QuickSubMenuEntryComponent('Telnet', _('Setup Telnet'), _('Setup Telnet')))
		self['sublist'].l.setList(self.sublist)

	def Qmount(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent('Network Mount Manager', _('Manage network mounts'), _('Setup your network mounts.')))
		self.sublist.append(QuickSubMenuEntryComponent('Mount again', _('Mount your network shares again'), _('Attempt to recover lost mounts (in background).')))
		self.sublist.append(QuickSubMenuEntryComponent('Network Browser', _('Search for network shares'), _('Search for network shares.')))
		self.sublist.append(QuickSubMenuEntryComponent('Device Mount Manager', _('Mounts Devices'), _('Setup your Device mounts (USB, HDD, others...)')))
		self.sublist.append(QuickSubMenuEntryComponent("fstab Editor", _("View or edit fstab"), _("View or Edit your device mounts in etc/fstab.")))
		self['sublist'].l.setList(self.sublist)

	def Qsoftcam(self):
		self.sublist = []
		if Check_Softcam():
			self.sublist.append(QuickSubMenuEntryComponent('Softcam Panel', _('Control your Softcams'), _('Use the Softcam Panel to control your Cam. This let you start/stop/select a cam.')))
			self.sublist.append(QuickSubMenuEntryComponent('Softcam-Panel Setup', _('Softcam-Panel Setup'), _('Softcam-Panel Setup.')))
		if Softcam_Check():
			if SC:
				self.sublist.append(QuickSubMenuEntryComponent('Softcam Manager', _('Softcam Manager'), _('Select and control your Cam. This let you start/stop/select a cam.')))
				self.sublist.append(QuickSubMenuEntryComponent('Softcam Manager Settings', _('Softcam Manager Settings'), _('Settings for the Softcam Manager.')))
			elif SSC:
				self.sublist.append(QuickSubMenuEntryComponent('Softcam-Setup', _('Softcam Setup'), _('Select and control your Softcam. Here you can start/stop/select a softcam, and see ecm info.')))
		self.sublist.append(QuickSubMenuEntryComponent('Download Softcams', _('Download and install cam'), _('Shows available softcams. Here you can download and install them.')))
		if ECMINFOSETUP:
			self.sublist.append(QuickSubMenuEntryComponent('Ecm Info', _('Ecm Info setup'), _('Setup Ecm Info of the CCcamInfo plugin.')))
		self.sublist.append(QuickSubMenuEntryComponent("CCcam Info", _("Check your CCcam"), _("This plugin shows you the status of your CCcam.")))
		self.sublist.append(QuickSubMenuEntryComponent("OScam Info", _("Check your OScam"), _("This plugin shows you the status of your OScam.")))
		self['sublist'].l.setList(self.sublist)

	def Qavsetup(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent('AV Settings', _('Setup Videomode'), _('Setup your Video Mode, Video Output and other Video Settings.')))
		if AUTORES == True:
			self.sublist.append(QuickSubMenuEntryComponent('Auto Resolution', _('Auto Resolution switch'), _('Setup your preferences for the automatic resolution switch.')))
		if AUDIOSYNC == True:
			self.sublist.append(QuickSubMenuEntryComponent('Audio Sync', _('Setup Audio Sync'), _('Setup Audio Sync settings')))
		if AUTVOLADJ == True:
			self.sublist.append(QuickSubMenuEntryComponent('Automatic Volume Adjustment', _('Automatic Volume Adjustment settings'), _('Setup for Automatic Volume Adjustment between MPEG and AC3/DTS.')))
		self.sublist.append(QuickSubMenuEntryComponent('Auto Language', _('Auto Language Selection'), _('Select your Language for Audio/Subtitles.')))
		self.sublist.append(QuickSubMenuEntryComponent('Subtitle settings', _('Extensive subtitle settings'), _('Select your preference for color, size, position, delay and subtitle type.')))
		if VIDTUNE == True:
			self.sublist.append(QuickSubMenuEntryComponent('Testscreens', _('Test screens for your TV'), _('Tune your TV for the best result.')))
		if os.path.exists('/proc/stb/vmpeg/0/pep_apply') and VIDEOENH == True:
			self.sublist.append(QuickSubMenuEntryComponent('VideoEnhancement', _('VideoEnhancement Setup'), _('VideoEnhancement Setup.')))
		self.sublist.append(QuickSubMenuEntryComponent('Hdmi CEC', _('HDMI-CEC setup'), _('Setup your HDMI communication and preferences.')))
		self['sublist'].l.setList(self.sublist)

	def Qtuner(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent('Tuner Configuration', _('Setup tuner(s)'), _('Setup each tuner for your satellite system.')))
		if POSSETUP == True:
			self.sublist.append(QuickSubMenuEntryComponent('Positioner Setup', _('Setup rotor'), _('Setup your positioner for your satellite system.')))
		self.sublist.append(QuickSubMenuEntryComponent('Sundtek Control Center', _('Sundtek tuner Setup'), _('Configure your Sundtek tuner(s) or check/update the drivers.')))
		self.sublist.append(QuickSubMenuEntryComponent('Automatic Scan', _('Service Searching Automatically'), _('Automatic scan for services.')))
		self.sublist.append(QuickSubMenuEntryComponent('Manual Scan', _('Service Searching Manually'), _('Manual scan for services.')))
		self.sublist.append(QuickSubMenuEntryComponent('Fallback remote receiver setup', _('Setup for fallback remote receiver(s)'), _('Enable and setup your fallback remote receiver(s).')))
		if FASTSCAN == True:
			self.sublist.append(QuickSubMenuEntryComponent('Fast Scan', _('Fast Scan Service Searching'), _('Use Fast Scan to search for services.')))
		if BLINDSCAN == True:
			self.sublist.append(QuickSubMenuEntryComponent('Blind Scan', _('Blindscan Service Searching'), _('Scan for satellite services.')))
		if CABLESCAN == True:
			self.sublist.append(QuickSubMenuEntryComponent('Cable Scan', _('Cable Service Searching'), _('Scan for cable services.')))
		if MISPLSLCNSCAN == True:
			self.sublist.append(QuickSubMenuEntryComponent('MIS/PLS LCN Scan', _('MIS/PLS LCN Service Searching'), _('Scan for MIS/PLS LCN services.')))
		if TERRESTSCAN == True:
			self.sublist.append(QuickSubMenuEntryComponent('Terrestrial Scan', _('Terrestrial Service Searching'), _('Scan for terrestrial services.')))
		self.sublist.append(QuickSubMenuEntryComponent('Sat Finder', _('Search Sats'), _('Search Sats, check signal and lock.')))
		self['sublist'].l.setList(self.sublist)

	def Qsoftware(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent('Software Update', _('Online software update'), _('Check/Install online updates (you must have a working internet connection).')))
		if not getBoxType().startswith('az') and not getBoxType().startswith('dream') and not getBoxType().startswith('ebox'):
			self.sublist.append(QuickSubMenuEntryComponent('Flash Online', _('Flash Online a new image'), _('Flash on the fly your Receiver software.')))
		self.sublist.append(QuickSubMenuEntryComponent('Complete Backup', _('Backup your current image'), _('Backup your current image to HDD or USB. This will make a 1:1 copy of your box.')))
		self.sublist.append(QuickSubMenuEntryComponent('Backup Settings', _('AutoBackup Settings System'), _('Backup your current settings. This includes E2-setup, channels, network and all selected files.')))
#		self.sublist.append(QuickSubMenuEntryComponent('Restore Settings', _('Restore settings from a backup'), _('Restore your settings back from a backup. After restore the box will restart to activate the new settings.')))
		self.sublist.append(QuickSubMenuEntryComponent('Select Backup files', _('Choose the files to backup'), _('Here you can select which files should be added to backupfile. (default: E2-setup, channels, network).')))
		self.sublist.append(QuickSubMenuEntryComponent('Software Manager Setup', _('Manage your online update files'), _('Here you can select which files should be updated with a online update.')))
		self['sublist'].l.setList(self.sublist)

	def Qplugin(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent('Plugin Browser', _('Open the Plugin Browser'), _('Shows Plugins Browser. Here you can setup installed Plugins.')))
		self.sublist.append(QuickSubMenuEntryComponent('Download Plugins', _('Download and install Plugins'), _('Shows available plugins. Here you can download and install them.')))
		self.sublist.append(QuickSubMenuEntryComponent('Remove Plugins', _('Delete Plugins'), _('Delete and unstall Plugins. This will remove the Plugin from your box.')))
		self.sublist.append(QuickSubMenuEntryComponent('Plugin Filter', _('Setup Plugin filter'), _('Setup Plugin filter. Here you can select which Plugins are showed in the PluginBrowser.')))
		self.sublist.append(QuickSubMenuEntryComponent('IPK Installer', _('Install local extension'), _('Scan for local extensions and install them.')))
		self.sublist.append(QuickSubMenuEntryComponent('IPK Uninstaller', _('Uninstall *.ipk files'), _('Scan for installed .ipk packages, and uninstall a package.')))
		self['sublist'].l.setList(self.sublist)

	def Qharddisk(self):
		self.sublist = []
		self.sublist.append(QuickSubMenuEntryComponent('Harddisk Setup', _('Harddisk Setup'), _('Setup your Harddisk.')))
		self.sublist.append(QuickSubMenuEntryComponent('Initialization', _('Format HDD'), _('Format your Harddisk.')))
		self.sublist.append(QuickSubMenuEntryComponent('Filesystem Check', _('Check HDD'), _('Filesystem check your Harddisk.')))
		self['sublist'].l.setList(self.sublist)

	def ok(self):
		if self.menu > 0:
			self.okSubList()
		else:
			self.goRight()

	def okList(self):
		item = self['list'].getCurrent()
		if item[0] == _('Network'):
			self.GetNetworkInterfaces()
			self.Qnetwork()
		elif item[0] == _('System'):
			self.Qsystem()
		elif item[0] == _('Mounts'):
			self.Qmount()
		elif item[0] == _('Softcam'):
			self.Qsoftcam()
		elif item[0] == _('AV Setup'):
			self.Qavsetup()
		elif item[0] == _('Tuner Setup'):
			self.Qtuner()
		elif item[0] == _('Software Manager'):
			self.Qsoftware()
		elif item[0] == _('Plugins'):
			self.Qplugin()
		elif item[0] == _('Harddisk'):
			self.Qharddisk()
		self['sublist'].selectionEnabled(0)

	def okSubList(self):
		item = self['sublist'].getCurrent()
		if item[0] == _('Network Wizard'):
			self.session.open(NetworkWizard)
		elif item[0] == _('Network Adapter Selection'):
			self.session.open(NetworkAdapterSelection)
		elif item[0] == _('Network Interface'):
			self.session.open(AdapterSetup, self.activeInterface)
		elif item[0] == _('Network Restart'):
			self.session.open(RestartNetwork)
		elif item[0] == _('Network Services'):
			self.Qnetworkservices()
			self['sublist'].moveToIndex(0)
		elif item[0] == _('Samba'):
			self.session.open(NetworkSamba)
		elif item[0] == _('NFS'):
			self.session.open(NetworkNfs)
		elif item[0] == _('FTP'):
			self.session.open(NetworkFtp)
		elif item[0] == _('AFP'):
			self.session.open(NetworkAfp)
		elif item[0] == _('OpenVPN'):
			self.session.open(NetworkOpenvpn)
		elif item[0] == _('MiniDLNA'):
			self.session.open(NetworkMiniDLNA)
		elif item[0] == _('Inadyn'):
			self.session.open(NetworkInadyn)
		elif item[0] == _('SABnzbd'):
			self.session.open(NetworkSABnzbd)
		elif item[0] == _('uShare'):
			self.session.open(NetworkuShare)
		elif item[0] == _('Telnet'):
			self.session.open(NetworkTelnet)
		elif item[0] == _('VPN Changer'):
			self.session.open(VpnScreen)
		elif item[0] == _('PureVPN Manager'):
			self.session.open(PureVPNScreen)
		elif item[0] == _('VPN Manager'):
			self.session.open(VpnManagerScreen)
		elif item[0] == _('Customize'):
			self.openSetup('usage')
		elif item[0] == _('Display Settings'):
			self.openSetup('lcd')
		elif item[0] == _('LCD Skin Setup'):
			self.session.open(LcdSkinSelector)
		elif item[0] == _('Skin Setup'):
			self.session.open(SkinSelector)
		elif item[0] == _('User interface'):
			self.openSetup('userinterface')
		elif item[0] == _('Recording paths'):
			self.session.open(RecordPathsSettings)
		elif item[0] == _('Recording and Playback settings'):
			self.openSetup('recording')
		elif item[0] == _('Hotkey'):
			self.session.open(HotkeySetup)
		elif item[0] == _('EPG settings'):
			self.openSetup('epgsettings')
		elif item[0] == _('Language'):
			self.session.open(LanguageSelection)
		elif item[0] == _('Network Mount Manager'):
			self.session.open(AutoMountManager, None, plugin_path_networkbrowser)
		elif item[0] == _('Mount again'):
			AutoMount()
			self.session.open(MessageBox, _('Network Shares are Mounted again.'), MessageBox.TYPE_INFO, timeout=3)
		elif item[0] == _('Network Browser'):
			self.session.open(NetworkBrowser, None, plugin_path_networkbrowser)
		elif item[0] == _('Device Mount Manager'):
			self.session.open(DevicesMountPanel)
		elif item[0] == _("fstab Editor"):
			self.session.open(fstabViewer.fstabViewerScreen)
		elif item[0] == _('Softcam Panel'):
			self.session.open(SoftcamPanel)
		elif item[0] == _('Softcam-Panel Setup'):
			self.session.open(ShowSoftcamPanelExtensions)
		elif item[0] == _('Download Softcams'):
			self.session.open(ShowSoftcamPackages)
		elif item[0] == _('Softcam Manager'):
			self.session.open(ScNewSelection)
		elif item[0] == _('Softcam Manager Settings'):
			self.session.open(ScSetupScreen)
		elif item[0] == _('Softcam-Setup'):
			self.session.open(SoftcamSetup)
		elif item[0] == _('Ecm Info'):
			self.session.open(EcmInfoConfigMenu)
		elif item[0] == _("CCcam Info"):
			self.session.open(CCcamInfoMain)
		elif item[0] == _("OScam Info"):
			self.session.open(OscamInfoMenu)
		elif item[0] == _('AV Settings'):
			videoSetupMain(self.session)
		elif item[0] == _('Auto Resolution'):
			autoresSetup(self.session)
		elif item[0] == _('Auto Language'):
			self.openSetup('autolanguagesetup')
		elif item[0] == _('Subtitle settings'):
			self.openSetup('subtitlesetup')
		elif item[0] == _('Automatic Volume Adjustment'):
			self.session.open(AutomaticVolumeAdjustmentConfigScreen)
		elif item[0] == _('Audio Sync'):
			self.session.open(AC3LipSyncSetup, plugin_path_audiosync)
		elif item[0] == _('Testscreens'):
			self.session.open(VideoFinetune)
		elif item[0] == _('VideoEnhancement'):
			self.session.open(VideoEnhancementSetup)
		elif item[0] == _('Hdmi CEC'):
			if HDMICEC == True:
				self.session.open(HdmiCECSetupScreen)
			else:
				self.session.open(MessageBox, _('Sorry,\nHdmi CEC is not available for this box at the moment.'), MessageBox.TYPE_INFO, timeout=10)
		elif item[0] == _('Tuner Configuration'):
			self.session.open(NimSelection)
		elif item[0] == _('Positioner Setup'):
			self.PositionerMain()
		elif item[0] == _('Sundtek Control Center'):
			self.session.open(SundtekControlCenter)
		elif item[0] == _('Automatic Scan'):
			self.session.open(ScanSimple)
		elif item[0] == _('Manual Scan'):
			self.session.open(ScanSetup)
		elif item[0] == _('Fallback remote receiver setup'):
			self.session.open(SetupFallbacktuner)
		elif item[0] == _('Fast Scan'):
			FastScanMain(self.session)
		elif item[0] == _('Blind Scan'):
			BlindscanMain(self.session)
		elif item[0] == _('Cable Scan'):
			CableScanMain(self.session)
		elif item[0] == _('MIS/PLS LCN Scan'):
			MisPlsLcnScanMain(self.session)
		elif item[0] == _('Terrestrial Scan'):
			TerrestrialScanMain(self.session)
		elif item[0] == _('Sat Finder'):
			self.SatfinderMain()
		elif item[0] == _('Software Update'):
			self.session.open(SoftwarePanel)
		elif item[0] == _('Flash Online'):
			self.session.open(SelectImage)
		elif item[0] == _('Complete Backup'):
			if DFLASH == True:
				self.session.open(dFlash)
			else:
				self.session.open(ImageBackup)
		elif item[0] == _('Backup Settings'):
			self.session.open(Config)
#		elif item[0] == _('Restore Settings'):
#			self.backuppath = getBackupPath()
#			if not path.isdir(self.backuppath):
#				self.backuppath = getOldBackupPath()
#			self.backupfile = getBackupFilename()
#			self.fullbackupfilename = self.backuppath + '/' + self.backupfile
#			if os.path.exists(self.fullbackupfilename):
#				self.session.openWithCallback(self.startRestore, MessageBox, _('Are you sure you want to restore your %s %s backup?\nSTB will restart after the restore') % (getMachineBrand(), getMachineName()))
#			else:
#				self.session.open(MessageBox, _('Sorry no backups found!'), MessageBox.TYPE_INFO, timeout=10)
		elif item[0] == _('Select Backup files'):
			self.session.open(BackupSelection)
		elif item[0] == _('Software Manager Setup'):
			self.session.open(SoftwareManagerSetup)
		elif item[0] == _('Plugin Browser'):
			self.session.open(PluginBrowser)
		elif item[0] == _('Download Plugins'):
			self.session.open(PluginDownloadBrowser, 0)
		elif item[0] == _('Remove Plugins'):
			self.session.open(PluginDownloadBrowser, 1)
		elif item[0] == _('Plugin Filter'):
			self.session.open(PluginFilter)
		elif item[0] == _('IPK Installer'):
		    self.session.open(AddonsFileBrowser)
		elif item[0] == _('IPK Uninstaller'):
			try:
				self.session.open(Ipkuninstall)
			except:
				self.session.open(MessageBox, _('Sorry IPK-uninstaller is not installed!'), MessageBox.TYPE_INFO, timeout=10)
		elif item[0] == _('Harddisk Setup'):
			self.openSetup('harddisk')
		elif item[0] == _('Initialization'):
			self.session.open(HarddiskSelection)
		elif item[0] == _('Filesystem Check'):
			self.session.open(HarddiskFsckSelection)
		return

	def openSetup(self, dialog):
		self.session.openWithCallback(self.menuClosed, Setup, dialog)

	def menuClosed(self, *res):
		pass

	def GetNetworkInterfaces(self):
		self.adapters = [(iNetwork.getFriendlyAdapterName(x), x) for x in iNetwork.getAdapterList()]
		if not self.adapters:
			self.adapters = [(iNetwork.getFriendlyAdapterName(x), x) for x in iNetwork.getConfiguredAdapters()]
		if len(self.adapters) == 0:
			self.adapters = [(iNetwork.getFriendlyAdapterName(x), x) for x in iNetwork.getInstalledAdapters()]
		self.activeInterface = None
		for x in self.adapters:
			if iNetwork.getAdapterAttribute(x[1], 'up') is True:
				self.activeInterface = x[1]
				return

		return

	def PositionerMain(self):
		nimList = nimmanager.getNimListOfType('DVB-S')
		if len(nimList) == 0:
			self.session.open(MessageBox, _('No positioner capable frontend found.'), MessageBox.TYPE_ERROR)
		elif len(NavigationInstance.instance.getRecordings()) > 0:
			self.session.open(MessageBox, _('A recording is currently running. Please stop the recording before trying to configure the positioner.'), MessageBox.TYPE_ERROR)
		else:
			usableNims = []
			for x in nimList:
				configured_rotor_sats = nimmanager.getRotorSatListForNim(x)
				if len(configured_rotor_sats) != 0:
					usableNims.append(x)

			if len(usableNims) == 1:
				self.session.open(PositionerSetup, usableNims[0])
			elif len(usableNims) > 1:
				self.session.open(RotorNimSelection)
			else:
				self.session.open(MessageBox, _('No tuner is configured for use with a diseqc positioner!'), MessageBox.TYPE_ERROR)

	def SatfinderMain(self):
		ActiveNim = nimmanager.somethingConnected()
		if ActiveNim:
			if len(NavigationInstance.instance.getRecordings()) > 0:
				self.session.open(MessageBox, _('A recording is currently running. Please stop the recording before trying to start the satfinder.'), MessageBox.TYPE_ERROR)
			else:
				self.session.open(Satfinder)
		else:
			self.session.open(MessageBox, _('No active tuner found !!') + '\n' + _('Sat Finder can only work with an activated tuner.'), MessageBox.TYPE_ERROR)

	def backupfiles_choosen(self, ret):
		config.plugins.configurationbackup.backupdirs.save()
		config.plugins.configurationbackup.save()
		config.save()

	def backupDone(self, retval=None):
		if retval is True:
			self.session.open(MessageBox, _('Backup done.'), MessageBox.TYPE_INFO, timeout=10)
		else:
			self.session.open(MessageBox, _('Backup failed.'), MessageBox.TYPE_INFO, timeout=10)

	def startRestore(self, ret=False):
		if ret == True:
			self.exe = True
			self.session.open(RestoreScreen, runRestore=True)


def QuickMenuEntryComponent(name, description, long_description=None, width=540):
	pngname = name.replace(' ', '_')
	png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/' + pngname + '.png')
	if png is None:
		png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/default.png')
	sz_w = getDesktop(0).size().width()
	if sz_w and sz_w == 1920:
		width *= 1.5
		return [_(name),
		MultiContentEntryText(pos=(90, 2), size=(width - 90, 40), font=0, text=_(name)),
		MultiContentEntryText(pos=(90, 42), size=(width - 90, 30), font=1, text=_(description)),
		MultiContentEntryPixmapAlphaTest(pos=(15, 8), size=(60, 60), flags=BT_SCALE, png=png),
		_(long_description)]
	elif sz_w > 720:
		return [_(name),
		MultiContentEntryText(pos=(80, 2), size=(width - 90, 38), font=0, text=_(name)),
		MultiContentEntryText(pos=(80, 32), size=(width - 90, 30), font=1, text=_(description)),
		MultiContentEntryPixmapAlphaTest(pos=(15, 8), size=(60, 60), png=png),
		_(long_description)]
	else:
		return [_(name),
		MultiContentEntryText(pos=(60, 3), size=(width - 60, 25), font=0, text=_(name)),
		MultiContentEntryText(pos=(60, 25), size=(width - 60, 20), font=1, text=_(description)),
		MultiContentEntryPixmapAlphaTest(pos=(10, 5), size=(40, 40), png=png),
		_(long_description)]


def QuickSubMenuEntryComponent(name, description, long_description=None, width=540):
	sz_w = getDesktop(0).size().width()
	if sz_w and sz_w == 1920:
		width *= 1.5
		return [_(name),
		MultiContentEntryText(pos=(15, 2), size=(width - 15, 40), font=0, text=_(name)),
		MultiContentEntryText(pos=(15, 42), size=(width - 15, 30), font=1, text=_(description)),
		_(long_description)]
	elif sz_w > 720:
		return [_(name),
		MultiContentEntryText(pos=(15, 2), size=(width - 15, 40), font=0, text=_(name)),
		MultiContentEntryText(pos=(15, 32), size=(width - 15, 30), font=1, text=_(description)),
		_(long_description)]
	else:
		return [_(name),
		MultiContentEntryText(pos=(10, 3), size=(width - 10, 25), font=0, text=_(name)),
		MultiContentEntryText(pos=(10, 25), size=(width - 10, 20), font=1, text=_(description)),
		_(long_description)]


class QuickMenuList(MenuList):

	def __init__(self, list, enableWrapAround=True):
		MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
		sz_w = getDesktop(0).size().width()
		if sz_w and sz_w == 1920:
			self.l.setFont(0, gFont("Regular", 32))
			self.l.setFont(1, gFont("Regular", 24))
			self.l.setItemHeight(78)
		else:
			self.l.setFont(0, gFont("Regular", 24))
			self.l.setFont(1, gFont("Regular", 16))
			self.l.setItemHeight(55)


class QuickMenuSubList(MenuList):

	def __init__(self, sublist, enableWrapAround=True):
		MenuList.__init__(self, sublist, enableWrapAround, eListboxPythonMultiContent)
		sz_w = getDesktop(0).size().width()
		if sz_w and sz_w == 1920:
			self.l.setFont(0, gFont("Regular", 32))
			self.l.setFont(1, gFont("Regular", 24))
			self.l.setItemHeight(78)
		else:
			self.l.setFont(0, gFont("Regular", 24))
			self.l.setFont(1, gFont("Regular", 16))
			self.l.setItemHeight(55)


class QuickMenuDevices(Screen):
	skin = '\n\t\t<screen name="QuickMenuDevices" position="center,center" size="840,525" title="Devices" flags="wfBorder">\n\t\t<widget source="devicelist" render="Listbox" position="30,46" size="780,450" font="Regular;16" scrollbarMode="showOnDemand" transparent="1" backgroundColorSelected="grey" foregroundColorSelected="black">\n\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t{"template": [\n\t\t\t\t MultiContentEntryText(pos = (90, 0), size = (600, 30), font=0, text = 0),\n\t\t\t\t MultiContentEntryText(pos = (110, 30), size = (600, 50), font=1, flags = RT_VALIGN_TOP, text = 1),\n\t\t\t\t MultiContentEntryPixmapAlphaBlend(pos = (0, 0), size = (80, 80), png = 2),\n\t\t\t\t],\n\t\t\t\t"fonts": [gFont("Regular", 24),gFont("Regular", 20)],\n\t\t\t\t"itemHeight": 85\n\t\t\t\t}\n\t\t\t</convert>\n\t</widget>\n\t<widget name="lab1" zPosition="2" position="126,92" size="600,40" font="Regular;22" halign="center" backgroundColor="black" transparent="1" />\n\t</screen> '

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _('Devices'))
		self['lab1'] = Label()
		self.devicelist = []
		self['devicelist'] = List(self.devicelist)
		self['actions'] = ActionMap(['WizardActions'], {'back': self.close})
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.updateList2)
		self.updateList()

	def updateList(self, result=None, retval=None, extra_args=None):
		scanning = _('Wait please while scanning for devices...')
		self['lab1'].setText(scanning)
		self.activityTimer.start(10)

	def updateList2(self):
		self.activityTimer.stop()
		self.devicelist = []
		list2 = []
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if not parts:
				continue
			device = parts[3]
			if not search('sd[a-z][1-9]', device):
				continue
			if device in list2:
				continue
			self.buildMy_rec(device)
			list2.append(device)

		f.close()
		self['devicelist'].list = self.devicelist
		if len(self.devicelist) == 0:
			self['lab1'].setText(_('No Devices Found !!'))
		else:
			self['lab1'].hide()

	def buildMy_rec(self, device):
		device2 = device[:-(len(device) - 3)]	#strip device number
		devicetype = path.realpath('/sys/block/' + device2 + '/device')
		name = 'USB: '
		mypixmap = '/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/dev_usbstick.png'
		model = file('/sys/block/' + device2 + '/device/model').read()
		model = str(model).replace('\n', '')
		des = ''
		if devicetype.find('/devices/pci') != -1:
			name = _('HARD DISK: ')
			mypixmap = '/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/dev_hdd.png'
		name = name + model

		from Components.Console import Console
		self.Console = Console()
		self.Console.ePopen("sfdisk -l /dev/sd? | grep swap | awk '{print $(NF-9)}' >/tmp/devices.tmp")
		sleep(0.5)
		f = open('/tmp/devices.tmp', 'r')
		swapdevices = f.read()
		f.close()
		swapdevices = swapdevices.replace('\n', '')
		swapdevices = swapdevices.split('/')
		f = open('/proc/mounts', 'r')
		for line in f.readlines():
			if line.find(device) != -1:
				parts = line.strip().split()
				d1 = parts[1]
				dtype = parts[2]
				rw = parts[3]
				break
				continue
			else:
				if device in swapdevices:
					parts = line.strip().split()
					d1 = _('None')
					dtype = 'swap'
					rw = _('None')
					break
					continue
				else:
					d1 = _('None')
					dtype = _('unavailable')
					rw = _('None')
		f.close()
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			if line.find(device) != -1:
				parts = line.strip().split()
				size = int(parts[2])
				if ((size / 1024) / 1024) > 1:
					des = _('Size: ') + str((size / 1024) / 1024) + _('GB')
				else:
					des = _('Size: ') + str(size / 1024) + _('MB')
			else:
				try:
					size = file('/sys/block/' + device2 + '/' + device + '/size').read()
					size = str(size).replace('\n', '')
					size = int(size)
				except:
					size = 0
				if (((size / 2) / 1024) / 1024) > 1:
					des = _('Size: ') + str(((size / 2) / 1024) / 1024) + _('GB')
				else:
					des = _('Size: ') + str((size / 2) / 1024) + _('MB')
		f.close()
		if des != '':
			if rw.startswith('rw'):
				rw = ' R/W'
			elif rw.startswith('ro'):
				rw = ' R/O'
			else:
				rw = ''
			des += '\t' + _('Mount: ') + d1 + '\n' + _('Device: ') + ' /dev/' + device + '\t' + _('Type: ') + dtype + rw
			png = LoadPixmap(mypixmap)
			res = (name, des, png)
			self.devicelist.append(res)
