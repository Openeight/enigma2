from Plugins.Plugin import PluginDescriptor
from Screens.PluginBrowser import *
from Screens.Ipkg import Ipkg
from Components.SelectionList import SelectionList
from Screens.NetworkSetup import *
from enigma import *
from boxbranding import getMachineBrand, getMachineName
from Screens.Standby import *
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap 
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Tools.BoundFunction import boundFunction
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from Components.Sources.List import List
from Components.MenuList import MenuList
from Components.FileList import FileList
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap
from Components.config import ConfigSubsection, ConfigInteger, ConfigText, getConfigListEntry, ConfigSelection,  ConfigIP, ConfigYesNo, ConfigSequence, ConfigNumber, NoSave, ConfigEnableDisable, configfile
from Components.ConfigList import ConfigListScreen
from Components.Sources.StaticText import StaticText 
from Components.Sources.Progress import Progress
from Components.Button import Button
from Components.ActionMap import ActionMap
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Plugins.SystemPlugins.SoftwareManager.ImageBackup import ImageBackup
from Addons import AddonsFileBrowser
from Plugins.SystemPlugins.SoftwareManager.BackupRestore import BackupScreen, RestoreScreen, BackupSelection, getBackupPath, getBackupFilename, RestoreMenu
from Plugins.SystemPlugins.SoftwareManager.Flash_online import FlashOnline
from Screens.SkinSetup import SkinSetup
from Screens.Ipkuninstall import Ipkuninstall
from os import system, listdir, symlink, unlink, readlink, path as os_path, stat, mkdir, popen, makedirs, access, rename, remove, W_OK, R_OK, F_OK, chmod, walk, getcwd, chdir, statvfs
from __init__ import _

import os
import sys
import re
import ServiceReference
import time
import datetime
inEXTRASPanel = None

config.softcam = ConfigSubsection()
config.softcam.actCam = ConfigText(visible_width = 200)
config.softcam.actCam2 = ConfigText(visible_width = 200)
config.softcam.waittime = ConfigSelection([('0',_("dont wait")),('1',_("1 second")), ('5',_("5 seconds")),('10',_("10 seconds")),('15',_("15 seconds")),('20',_("20 seconds")),('30',_("30 seconds"))], default='15')
config.plugins.extraspanel_redpanel = ConfigSubsection()
config.plugins.extraspanel_redpanel.enabled = ConfigYesNo(default=True)
config.plugins.extraspanel_redpanel.enabledlong = ConfigYesNo(default=False)
config.plugins.extraspanel_yellowkey = ConfigSubsection()
config.plugins.extraspanel_yellowkey.list = ConfigSelection([('0',_("Audio Selection")),('1',_("Default (Timeshift)")), ('2',_("Toggle Pillarbox <> Pan&Scan"))])
config.plugins.showextraspanelextensions = ConfigYesNo(default=False)
config.plugins.extraspanel_frozencheck = ConfigSubsection()
config.plugins.extraspanel_frozencheck.list = ConfigSelection([('0',_("Off")),('1',_("1 min.")), ('5',_("5 min.")),('10',_("10 min.")),('15',_("15 min.")),('30',_("30 min."))])
if os.path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/plugin.pyo") is True:
	try:
		from Plugins.Extensions.MultiQuickButton.plugin import *
	except:
		pass
		
if os.path.isfile("/usr/lib/enigma2/python/Plugins/PLi/SoftcamSetup/plugin.pyo") is True:
	try:
		from Plugins.PLi.SoftcamSetup import Sc
	except:
		pass
		
if os.path.isfile("/usr/lib/enigma2/python/Plugins/SystemPlugins/SoftwareManager/plugin.pyo") is True:
	try:
		from Plugins.SystemPlugins.SoftwareManager.plugin import PacketManager
	except:
		pass


from Plugins.Extensions.ExtrasPanel.CronManager import *
from Plugins.Extensions.ExtrasPanel.ScriptRunner import *
from Plugins.Extensions.ExtrasPanel.MountManager import *
from Plugins.Extensions.ExtrasPanel.SoftcamPanel import *
from Plugins.Extensions.ExtrasPanel.CamStart import *
from Plugins.Extensions.ExtrasPanel.CamCheck import *
from Plugins.Extensions.ExtrasPanel.sundtek import *
from Plugins.Extensions.ExtrasPanel.SwapManager import Swap, SwapAutostart
from Plugins.Extensions.ExtrasPanel.SoftwarePanel import SoftwarePanel
from Plugins.Extensions.ExtrasPanel.XTDVBNTPTime import *

def Check_Softcam():
	found = False
	for x in os.listdir('/etc/init.d'):
		if x.find('softcam.') > -1 and x <> 'softcam.None':
			found = True
			break;
	return found

# Hide Softcam-Panel Setup when no softcams installed
if not Check_Softcam() and (config.plugins.showextraspanelextensions.getValue() or config.plugins.extraspanel_redpanel.enabledlong.getValue()):
	config.plugins.showextraspanelextensions.setValue(False)
	config.plugins.extraspanel_redpanel.enabledlong.setValue(False)
	config.plugins.showextraspanelextensions.save()
	config.plugins.extraspanel_redpanel.save()

# Hide Keymap selection when no other keymaps installed.
if config.usage.keymap.getValue() != eEnv.resolve("${datadir}/enigma2/keymap.xml"):
	if not os.path.isfile(eEnv.resolve("${datadir}/enigma2/keymap.mqb")) and config.usage.keymap.getValue() == eEnv.resolve("${datadir}/enigma2/keymap.mqb"):
		setDefaultKeymap()
        if not os.path.isfile(eEnv.resolve("${datadir}/enigma2/keymap.usr")) and config.usage.keymap.getValue() == eEnv.resolve("${datadir}/enigma2/keymap.usr"):
		setDefaultKeymap()
	if not os.path.isfile(eEnv.resolve("${datadir}/enigma2/keymap.ntr")) and config.usage.keymap.getValue() == eEnv.resolve("${datadir}/enigma2/keymap.ntr"):
		setDefaultKeymap()
	if not os.path.isfile(eEnv.resolve("${datadir}/enigma2/keymap.u80")) and config.usage.keymap.getValue() == eEnv.resolve("${datadir}/enigma2/keymap.u80"):
		setDefaultKeymap()
		
def setDefaultKeymap():
	print "[Extras-Panel] Set Keymap to Default"
	config.usage.keymap.setValue(eEnv.resolve("${datadir}/enigma2/keymap.xml"))
	config.save()

# edit bb , touch commands.getouput with this def #
def command(comandline, strip=1):
  comandline = comandline + " >/tmp/command.txt"
  os.system(comandline)
  text = ""
  if os.path.exists("/tmp/command.txt") is True:
    file = open("/tmp/command.txt", "r")
    if strip == 1:
      for line in file:
        text = text + line.strip() + '\n'
    else:
      for line in file:
        text = text + line
        if text[-1:] != '\n': text = text + "\n"
    file.close()
  # if one or last line then remove linefeed
  if text[-1:] == '\n': text = text[:-1]
  comandline = text
  os.system("rm /tmp/command.txt")
  return comandline

boxversion = getBoxType()
machinename = getMachineName()
machinebrand = getMachineBrand()

EXTRAS_Panel_Version = 'Eight Panel V1.0'
print "[eXTrAs-Panel] machinebrand: %s"  % (machinebrand)
print "[eXTrAs-Panel] machinename: %s"  % (machinename)
print "[eXTrAs-Panel] boxversion: %s"  % (boxversion)
panel = open("/tmp/extraspanel.ver", "w")
panel.write(EXTRAS_Panel_Version + '\n')
panel.write("Machinebrand: %s " % (machinebrand)+ '\n')
panel.write("Machinename: %s " % (machinename)+ '\n')
panel.write("Boxversion: %s " % (boxversion)+ '\n')
try:
	panel.write("Keymap: %s " % (config.usage.keymap.getValue())+ '\n')
except:
	panel.write("Keymap: keymap file not found !!" + '\n')
panel.close()
if boxversion == "inihde" and machinename.lower() == "xpeedlx":
	f1=open('/etc/hostname', "r")
	hostname = f1.read()
	f1.close()
	if not hostname[:7] == "xpeedlx":
		f=open('/etc/hostname', "w")
		f.write('xpeedlx\n')
		f.close()
		ff=open('/etc/model', "w")
		ff.write('xpeedlx\n')
		ff.close()
elif boxversion == "xp1000" and machinename.lower() == "sf8 hd":
	f1=open('/etc/hostname', "r")
	hostname = f1.read()
	f1.close()
	if not hostname[:3] == "sf8":
		f=open('/etc/hostname', "w")
		f.write('sf8\n')
		f.close()
		ff=open('/etc/model', "w")
		ff.write('sf8 hd\n')
		ff.close()

ExitSave = "[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save")


class ConfigPORT(ConfigSequence):
	def __init__(self, default):
		ConfigSequence.__init__(self, seperator = ".", limits = [(1,65535)], default = default)

def main(session, **kwargs):
		session.open(Extraspanel)

def Apanel(menuid, **kwargs):
	if menuid == "mainmenu":
		return [("eXTrAs panel", main, "Extraspanel", 11)]
	else:
		return []

def camstart(reason, **kwargs):
	if not config.plugins.extraspanel_frozencheck.list.getValue() == '0':
		CamCheck()
	try:
		f = open("/proc/stb/video/alpha", "w")
		f.write(str(config.osd.alpha.getValue()))
		f.close()
	except:
		print "[Extras-Panel] failed to write /proc/stb/video/alpha"

	try:
		if config.softcam.camstartMode.getValue() == "0":
			global timerInstance
			if timerInstance is None:
				timerInstance = CamStart(None)
			timerInstance.startTimer()
	except:
		print "[Extras-Panel] failed to run CamStart"

def Plugins(**kwargs):
	return [
	#// autostart
	PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART,PluginDescriptor.WHERE_AUTOSTART],fnc = camstart),
	#// DVBNTPautostart
        PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART,PluginDescriptor.WHERE_AUTOSTART],fnc = DVBNTPautostart),
	#// SwapAutostart
	PluginDescriptor(where = [PluginDescriptor.WHERE_SESSIONSTART,PluginDescriptor.WHERE_AUTOSTART],fnc = SwapAutostart),
	#// show Extraspanel in EXTENSIONS Menu
	PluginDescriptor(name="Eight Panel", description="Eight panel GUI 12/11/2012", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc = main) ]



#############------- SKINS --------############################

MENU_SKIN = """<screen name="Extraspanel" position="center,center" size="500,370" title="Extra Panel" >
	<widget source="global.CurrentTime" render="Label" position="0, 340" size="500,24" font="Regular;20" foregroundColor="#FFFFFF" halign="right" transparent="1" zPosition="5">
		<convert type="ClockToText">>Format%H:%M:%S</convert>
	</widget>
	<eLabel backgroundColor="#56C856" position="0,330" size="500,1" zPosition="0" />
	<widget source="list" render="Listbox" position="10,25" size="500,280" scrollbarMode="showOnDemand" zPosition="1" transparent="1">
                <convert type="TemplatedMultiContent">
				{"template": [
						MultiContentEntryText(pos = (0, 5), size = (520, 28), font=0, text = 0), # menu_entry
						MultiContentEntryText(pos = (0, 35), size = (520, 22), font=1, text = 2), # menu_entry_description
					],
				"fonts": [gFont("Regular",24),gFont("Regular",16)],
				"itemHeight": 70
				}
	 	</convert>
        </widget>
	<widget name="label1" position="10,340" size="490,25" font="Regular;20" transparent="1" foregroundColor="#f2e000" halign="left" />
</screen>"""

CONFIG_SKIN = """<screen position="center,center" size="600,440" title="PANEL Config" >
	<widget name="config" position="10,10" size="580,377" enableWrapAround="1" scrollbarMode="showOnDemand" />
	<widget name="labelExitsave" position="90,410" size="420,25" halign="center" font="Regular;20" transparent="1" foregroundColor="#f2e000" />
</screen>"""

INFO_SKIN =  """<screen name="Panel-Info"  position="center,center" size="730,400" title="PANEL-Info" >
	<widget name="label2" position="0,10" size="730,25" font="Regular;20" transparent="1" halign="center" foregroundColor="#f2e000" />
	<widget name="label1" position="10,45" size="710,350" font="Console;20" zPosition="1" backgroundColor="#251e1f20" transparent="1" />
</screen>"""

INFO_SKIN2 =  """<screen name="PANEL-Info2"  position="center,center" size="530,400" title="PANEL-Info" backgroundColor="#251e1f20">
	<widget name="label1" position="10,50" size="510,340" font="Regular;15" zPosition="1" backgroundColor="#251e1f20" transparent="1" />
</screen>"""

#g
from Screens.PiPSetup import PiPSetup
from Screens.InfoBarGenerics import InfoBarPiP
#g

class Extraspanel(Screen, InfoBarPiP):
	servicelist = None
	def __init__(self, session, services = None):
		Screen.__init__(self, session)
		self.session = session
		self.skin = MENU_SKIN
		self.onShown.append(self.setWindowTitle)
		self.service = None
		global pluginlist
		global videomode
		global infook
		global INFOCONF
		global menu
		INFOCONF = 0
		pluginlist="False"
		try:
			print '[Extras-Panel] SHOW'
			global inEXTRASPanel
			inEXTRASPanel = self
		except:
			print '[Extras-Panel] Error Hide'

		if services is not None:
			self.servicelist = services
		else:
			self.servicelist = None

		self["actions"] = ActionMap(["SetupActions", "DirectionActions", "ColorActions"],
			{
				"cancel": self.close, #self.Exit,
				"upUp": self.up,
				"downUp": self.down,
				"ok": self.okpress,
			}, 1)
		
		self["label1"] = Label(EXTRAS_Panel_Version)
		self.list = []
		self['list'] = List(self.list)
		self.onLayoutFinish.append(self.HomeMenulist)
		menu = 0

	def HomeMenulist(self):
		self.mylist = []
		self.mylist.append(((_('Backup/Flash'), 'BackupFlashManager', _('Backup your Image/Settings or Flash a new Image'))))
		if Check_Softcam():
			self.mylist.append(((_('Cam Setup'), 'CamSetup', _('select your favourite cam'))))
		self.mylist.append(((_('Image Update'), 'ImageUpdate', _('Software-Updates and Feed state'))))
		self.mylist.append(((_('Image Tools'), 'ImageTools', _('Image-Tools'))))
		self.mylist.append(((_('Infos'), 'Infos', _('Infos...'))))
		#self.mylist.append(((_('Skin Setup'), 'SkinSetup', _('Change your Skin/Gui and Skin settings'))))
		self['list'].setList(self.mylist)

	def setWindowTitle(self):
		self.setTitle(_("Eight Panel"))

	def up(self):
		#self["Mlist"].up()
		pass

	def down(self):
		#self["Mlist"].down()
		pass

	def left(self):
		pass

	def right(self):
		pass

	def Red(self):
		self.showExtensionSelection1(Parameter="run")
		pass

	def Green(self):
		#// Not used
		pass

	def yellow(self):
		#// Not used
		pass

	def blue(self):
		#// Not used
		pass

	def cancel(self):
		self.close()
 
#        def layoutFinished(self):
#                idx = -1
#                self['list'].index = idx

	def Exit(self):
		#// Exit Extraspanel when pressing the EXIT button or go back to the MainMenu
		global menu
		if menu == 0:
			try:
				self.service = self.session.nav.getCurrentlyPlayingServiceReference()
				service = self.service.toCompareString()
				servicename = ServiceReference.ServiceReference(service).getServiceName().replace('\xc2\x87', '').replace('\xc2\x86', '').ljust(16)
				print '[Extras-Panel] HIDE'
				global inEXTRASPanel
				inEXTRASPanel = None
			except:
				print '[Extras-Panel] Error Hide'
			self.close()
		elif menu == 1:
			self["Mlist"].moveToIndex(0)
			self["Mlist"].l.setList(self.oldmlist)
			menu = 0
			self["label1"].setText(EXTRAS_Panel_Version)
		elif menu == 2:
			self["Mlist"].moveToIndex(0)
			self["Mlist"].l.setList(self.oldmlist1)
			menu = 1
			self["label1"].setText("Infos")
		else:
			pass

	def okpress(self):
		#// Menu Selection

		global INFOCONF
#		menu = self['list'].l.getCurrentSelection()[0][2]
                current = self['list'].getCurrent()
                if current:
                        name = current[0]
                        menu = current[1]
		if menu == "BackupFlashManager":
			self.BackupFlashManager()
		elif menu == "BackupImage":
			self.session.open(ImageBackup)
		elif menu == "FlashImage":
			self.session.open(FlashOnline)
		elif menu == "BackupSettings":
			self.session.openWithCallback(self.backupDone,BackupScreen, runBackup = True)
		elif menu == "RestoreSettings":
			self.backuppath = getBackupPath()
			self.backupfile = getBackupFilename()
			self.fullbackupfilename = self.backuppath + "/" + self.backupfile
			if os_path.exists(self.fullbackupfilename):
				self.session.openWithCallback(self.startRestore, MessageBox, _("Are you sure you want to restore your STB backup?\nSTB will restart after the restore"), default = False)
			else:
				self.session.open(MessageBox, _("Sorry no backups found!"), MessageBox.TYPE_INFO, timeout = 10)
		elif menu == "BackupFiles":
			self.session.openWithCallback(self.backupfiles_choosen,BackupSelection)
		elif menu == "BackupLocation":
					parts = [ (r.description, r.mountpoint, self.session) for r in harddiskmanager.getMountedPartitions(onlyhotplug = False)]
					for x in parts:
						if not access(x[1], F_OK|R_OK|W_OK) or x[1] == '/':
							parts.remove(x)
					if len(parts):
						self.session.openWithCallback(self.backuplocation_choosen, ChoiceBox, title = _("Please select medium to use as backup location"), list = parts)
								
		elif menu == "CamSetup":
			self.session.open(Sc.ScNewSelection)
		elif menu == "AdvancedRestore":
		        self.session.open(RestoreMenu, self.skin)	
                elif menu == "SkinSetup":
			self.session.open(SkinSetup)
		elif menu == "ImageTools":
			self.Plugins()
		elif menu == "Pluginbrowser":
			self.session.open(PluginBrowser)
		elif menu == "Infos":
			self.Infos()
		elif menu == "InfoPanel":
			self.session.open(Info, "InfoPanel")
		elif menu == "Info":
			self.session.open(Info, "Sytem_info")
		elif menu == "Default":
			self.session.open(Info, "Default")
		elif menu == "FreeSpace":
			self.session.open(Info, "FreeSpace")
		elif menu == "Network":
			self.session.open(Info, "Network")
		elif menu == "Mounts":
			self.session.open(Info, "Mounts")
		elif menu == "Kernel":
			self.session.open(Info, "Kernel")
		elif menu == "Ram":
			self.session.open(Info, "Free")
		elif menu == "Cpu":
			self.session.open(Info, "Cpu")
		elif menu == "Top":
			self.session.open(Info, "Top")
		elif menu == "MemInfo":
			self.session.open(Info, "MemInfo")
		elif menu == "Module":
			self.session.open(Info, "Module")
		elif menu == "Mtd":
			self.session.open(Info, "Mtd")
		elif menu == "Partitions":
			self.session.open(Info, "Partitions")
		elif menu == "Swap":
			self.session.open(Info, "Swap")
		elif menu == "System_Info":
			self.System()
		elif menu == "CronManager":
			self.session.open(CronManager)	
		elif menu == "JobManager":
			self.session.open(ScriptRunner)
		elif menu == "SoftcamPanel":
			self.session.open(SoftcamPanel)
		elif menu == "SoftwareManager":
			self.Software_Manager()
		elif menu == "ImageUpdate":
			self.session.open(SoftwarePanel)
		elif menu == "MultiQuickButton":
			sz_w = getDesktop(0).size().width()
			from Components.PluginComponent import plugins
			plugin = _('MultiQuickbutton')
			for p in plugins.getPlugins(where=[PluginDescriptor.WHERE_PLUGINMENU]):
				if 'MultiQuickbutton' == str(p.name):
					plugin = p
			if plugin is not None and sz_w == 1280:
				plugin(session=self.session)
			else:
				self.session.open(MessageBox, _('Sorry:\nET-MultiQuickButton supports only HD skins with 1280x720px'), MessageBox.TYPE_INFO, timeout=10)
		elif menu == "PacketManager":
			self.session.open(PacketManager, self.skin)
		elif menu == "DVB-NTP-Time":
			from Plugins.Extensions.ExtrasPanel.XTDVBNTPTime import *
                        self.session.open(XTDVBNTPTime)
		elif menu == 'IPK-installManager':	
			self.session.open(AddonsFileBrowser)
		elif menu == 'IPK-uninstaller':	
			self.session.open(Ipkuninstall)	
		elif menu == "MountManager":
			self.session.open(DevicesMountPanel)
		elif menu == "SundtekControlCenter":
			self.session.open(SundtekControlCenter)
		elif menu == "SwapManager":
			self.session.open(Swap)
		elif menu == "RedPanel":
			self.session.open(RedPanel)
		elif menu == "Yellow-Key-Action":
			self.session.open(YellowPanel)
		elif menu == "Softcam-Panel Setup":
			self.session.open(ShowSoftcamPanelExtensions)
		elif menu == "KeymapSel":
			self.session.open(KeymapSel)
		else:
			pass

	def Plugins(self):
		#// Create Plugin Menu
		self["label1"].setText(_("Image Tools"))
		self.mylist = [] 
                self.mylist.append(((_('Keymap Selection'), 'KeymapSel', _('change your Keymap: *.mqb, *.usr, *.ntr, *.xml, *.u80'))))			
		self.mylist.append(((_('Mount Manager'), 'MountManager', _('Mount-Manager...'))))
		self.mylist.append(((_('Cron Manager'), 'CronManager', _('Cron-Manager...'))))
		self.mylist.append(((_('Job Manager'), 'JobManager', _('Job-Manager...'))))
		self.mylist.append(((_('Swap Manager'), 'SwapManager', _('Swap-Manager...'))))
		self.mylist.append(((_('IPK-install Manager'), 'IPK-installManager', _('install *.ipk, *.tar.gz files'))))
		self.mylist.append(((_('IPK-uninstaller'), 'IPK-uninstaller', _('uninstall *.ipk files'))))
		self.mylist.append(((_('Sundtek Control-Center'), 'SundtekControlCenter', _('select your Sundtek USB-Tuner ...'))))
		self.mylist.append(((_('Packet Manager'), 'PacketManager', _('show all Packages'))))		
		if os.path.isfile("/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/plugin.pyo") is True:
			self.mylist.append(((_('Multi Quick Button'), 'MultiQuickButton', _('change the button functions of your remote control'))))
		self.mylist.append(((_('DVB-NTP-Time'), 'DVB-NTP-Time', _('Check and set DVB Time'))))
		self['list'].setList(self.mylist)

	def Infos(self):
		#// Create Infos Menu
		self["label1"].setText(_("Infos"))
		self.mylist = []
		self.mylist.append(((_('Info Panel'), 'InfoPanel', _('Info-Panel...'))))
		self.mylist.append(((_('Default'), 'Default', _('Default'))))
		self.mylist.append(((_('Free Space'), 'FreeSpace', _('Free-Space...'))))
		self.mylist.append(((_('Kernel'), 'Kernel', _('Kernel...'))))
		self.mylist.append(((_('Mounts'), 'Mounts', _('Mounts...'))))
		self.mylist.append(((_('Network'), 'Network', _('Network...'))))
		self.mylist.append(((_('Ram'), 'Ram', _('Ram...'))))
		self.mylist.append(((_('System Info'), 'System_Info', _('System Information...'))))
		self['list'].setList(self.mylist)
		
	def SkinSetup(self):
		from Screens.SkinSetup import SkinSetup
		return SkinSetup

	def System(self):
		#// Create System Menu
		self["label1"].setText(_("System Info"))
		self.mylist = []
		self.mylist.append(((_('Cpu'), 'Cpu', _('Cpu...'))))
		self.mylist.append(((_('Memory Info'), 'MemInfo', _('Memory Info...'))))
		self.mylist.append(((_('Mtd'), 'Mtd', _('Mtd...'))))
		self.mylist.append(((_('Module'), 'Module', _('Module...'))))
		self.mylist.append(((_('Partitions'), 'Partitions', _('Partitions...'))))
		self.mylist.append(((_('Swap'), 'Swap', _('Swap...'))))
		self.mylist.append(((_('Top'), 'Top', _('Top...'))))
		self['list'].setList(self.mylist)

	def System_main(self):
		#// Create System Main Menu
		global menu
		menu = 1
		self["label1"].setText(_("System"))
		self.mylist = []
		self.mylist.append(((_('Info'), 'Info', _('Info...'))))
		self['list'].setList(self.mylist)

	def Software_Manager(self):
		#// Create Software Manager Menu
		global menu
		menu = 1
		self["label1"].setText(_("Software Manager"))
		self.mylist = []
		self.mylist.append(((_("Software Manager" ), 'SoftwareUpdate', ("software-update..."))))
		self.mylist.append(((_("Backup Settings" ), 'BackupSettings', ("backup your settings..."))))
		self.mylist.append(((_("Restore Settings" ), 'RestoreSettings', ("restore your settings"))))
		self.mylist.append(((_("advanced restore" ), 'AdvancedRestore', ("advanced restore"))))
		self.mylist.append(((_("Backup Files" ), 'BackupFiles', ("Choose backup-files"))))
		self.mylist.append(((_("Backup location" ), 'BackupLocation', ("choose backup location"))))
	#	self["Mlist"].moveToIndex(0)
		self['list'].setList(self.mylist)

	def BackupFlashManager(self):
		#// Create BackupFlash Manager Menu
		global menu
		menu = 1
		self["label1"].setText(_("Backup/Flash Manager"))
		self.mylist = []
		self.mylist.append(((_("Backup Image" ), 'BackupImage', _("Backup your Image"))))
		self.mylist.append(((_("Flash Online" ), 'FlashImage', _("Flash Online Image"))))
		self.mylist.append(((_("Backup Settings" ), 'BackupSettings', _("Backup your Settings"))))
		self.mylist.append(((_("Restore Settings" ), 'RestoreSettings', _("Restores your latest Settings Backup"))))
		self.mylist.append(((_("Advanced Restore" ), 'AdvancedRestore', _("Advanced Restore..."))))
		self.mylist.append(((_("Backup Files" ), 'BackupFiles', _("Choose Backup Files"))))
		self.mylist.append(((_("Backup location" ), 'BackupLocation', _("Choose Backup location"))))
		self['list'].setList(self.mylist)

	def backupfiles_choosen(self, ret):
		#self.backupdirs = ' '.join( config.plugins.configurationbackup.backupdirs.value )
		config.plugins.configurationbackup.backupdirs.save()
		config.plugins.configurationbackup.save()
		config.save()
    
	def backuplocation_choosen(self, option):
		oldpath = config.plugins.configurationbackup.backuplocation.getValue()
		if option is not None:
			config.plugins.configurationbackup.backuplocation.value = str(option[1])
		config.plugins.configurationbackup.backuplocation.save()
		config.plugins.configurationbackup.save()
		config.save()
		newpath = config.plugins.configurationbackup.backuplocation.getValue()
		if newpath != oldpath:
			self.createBackupfolders()
			
	def createBackupfolders(self):
		print "Creating backup folder if not already there..."
		self.backuppath = getBackupPath()
		try:
			if (os_path.exists(self.backuppath) == False):
				makedirs(self.backuppath)
		except OSError:
			self.session.open(MessageBox, _("Sorry, your backup destination is not writeable.\nPlease select a different one."), MessageBox.TYPE_INFO, timeout = 10)
		
			
	def backupDone(self,retval = None):
		if retval is True:
			self.session.open(MessageBox, _("Backup done."), MessageBox.TYPE_INFO, timeout = 10)
		else:
			self.session.open(MessageBox, _("Backup failed."), MessageBox.TYPE_INFO, timeout = 10)

	def startRestore(self, ret = False):
		if (ret == True):
			self.exe = True
			self.session.open(RestoreScreen, runRestore = True)

class KeymapSel(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = ["SetupInfo", "Setup" ]
		Screen.setTitle(self, _("Keymap Selection") + "...")
		self.setup_title =  _("Keymap Selection") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label("")
		self["labelInfo"] = Label(_("Copy your keymap to\n/usr/share/enigma2/keymap.usr"))

		mqbkey = eEnv.resolve("${datadir}/enigma2/keymap.mqb")
                usrkey = eEnv.resolve("${datadir}/enigma2/keymap.usr")
		ntrkey = eEnv.resolve("${datadir}/enigma2/keymap.ntr")
		u80key = eEnv.resolve("${datadir}/enigma2/keymap.u80")
		self.actkeymap = self.getKeymap(config.usage.keymap.getValue())
		keySel = [ ('keymap.xml',_("Default  (keymap.xml)"))]
		if os.path.isfile(mqbkey):
			keySel.append(('keymap.mqb',_("ET-MultiQuickButton  (keymap.mqb)")))
                if os.path.isfile(usrkey):
			keySel.append(('keymap.usr',_("User  (keymap.usr)")))
		if os.path.isfile(ntrkey):
			keySel.append(('keymap.ntr',_("Neutrino  (keymap.ntr)")))
		if os.path.isfile(u80key):
			keySel.append(('keymap.u80',_("UP80  (keymap.u80)")))
		if self.actkeymap == usrkey and not os.path.isfile(usrkey):
			setDefaultKeymap()
		if self.actkeymap == ntrkey and not os.path.isfile(ntrkey):
			setDefaultKeymap()
		if self.actkeymap == u80key and not os.path.isfile(u80key):
			setDefaultKeymap()
		self.keyshow = ConfigSelection(keySel)
		self.keyshow.setValue(self.actkeymap)

		self.onChangedEntry = [ ]
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
		self.createSetup()

		self["actions"] = ActionMap(["SetupActions", 'ColorActions'],
		{
			"ok": self.keySave,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
			"menu": self.keyCancel,
		}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def createSetup(self):
		self.editListEntry = None
		self.list = []
		self.list.append(getConfigListEntry(_("Use Keymap"), self.keyshow))
		
		self["config"].list = self.list
		self["config"].setList(self.list)

	def selectionChanged(self):
		self["status"].setText(self["config"].getCurrent()[0])

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
		self.selectionChanged()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def getCurrentDescription(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or ""

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

	def saveAll(self):
		config.usage.keymap.setValue(eEnv.resolve("${datadir}/enigma2/" + self.keyshow.getValue()))
		config.usage.keymap.save()
		configfile.save()
		if self.actkeymap != self.keyshow.getValue():
			self.changedFinished()

	def keySave(self):
		self.saveAll()
		self.close()

	def cancelConfirm(self, result):
		if not result:
			return
		for x in self["config"].list:
			x[1].cancel()
		self.close()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"))
		else:
			self.close()

	def getKeymap(self, file):
		return file[file.rfind('/') +1:]

	def changedFinished(self):
		self.session.openWithCallback(self.ExecuteRestart, MessageBox, _("Keymap changed, you need to restart the GUI") +"\n"+_("Do you want to restart now?"), MessageBox.TYPE_YESNO)
		self.close()

	def ExecuteRestart(self, result):
		if result:
			quitMainloop(3)
		else:
			self.close()

class RedPanel(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = "Setup"
		Screen.setTitle(self, _("RedPanel") + "...")
		self.setup_title =  _("RedPanel") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label(_(""))
		self["labelExitsave"] = Label("[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save"))

		self.onChangedEntry = [ ]
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
		self.createSetup()

		self["actions"] = ActionMap(["SetupActions", 'ColorActions'],
		{
			"ok": self.keySave,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
			"menu": self.keyCancel,
		}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def createSetup(self):
		self.editListEntry = None
		self.list = []
		self.list.append(getConfigListEntry(_("Show eXTrAs-Panel Red-key"), config.plugins.extraspanel_redpanel.enabled))
		self.list.append(getConfigListEntry(_("Show Softcam-Panel Red-key long"), config.plugins.extraspanel_redpanel.enabledlong))
		
		self["config"].list = self.list
		self["config"].setList(self.list)

	def selectionChanged(self):
		self["status"].setText(self["config"].getCurrent()[0])

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
		self.selectionChanged()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def getCurrentDescription(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or ""

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

	def saveAll(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()

	def keySave(self):
		self.saveAll()
		self.close()

	def cancelConfirm(self, result):
		if not result:
			return
		for x in self["config"].list:
			x[1].cancel()
		self.close()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"))
		else:
			self.close()

class YellowPanel(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = "Setup"
		Screen.setTitle(self, _("Yellow Key Action") + "...")
		self.setup_title = _("Yellow Key Action") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label("")
		self["labelExitsave"] = Label("[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save"))

		self.onChangedEntry = [ ]
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
		self.createSetup()

		self["actions"] = ActionMap(["SetupActions", 'ColorActions'],
		{
			"ok": self.keySave,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
			"menu": self.keyCancel,
		}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def createSetup(self):
		self.editListEntry = None
		self.list = []
		self.list.append(getConfigListEntry(_("Yellow Key Action"), config.plugins.extraspanel_yellowkey.list))
		
		self["config"].list = self.list
		self["config"].setList(self.list)

	def selectionChanged(self):
		self["status"].setText(self["config"].getCurrent()[0])

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
		self.selectionChanged()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def getCurrentDescription(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or ""

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

	def saveAll(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()

	def keySave(self):
		self.saveAll()
		self.close()

	def cancelConfirm(self, result):
		if not result:
			return
		for x in self["config"].list:
			x[1].cancel()
		self.close()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"))
		else:
			self.close()

class ShowSoftcamPanelExtensions(ConfigListScreen, Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.session = session
		self.skinName = "Setup"
		Screen.setTitle(self, _("Softcam-Panel Setup") + "...")
		self.setup_title = _("Softcam-Panel Setup") + "..."
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self["status"] = StaticText()
		self['footnote'] = Label("")
		self["description"] = Label("")
		self["labelExitsave"] = Label("[Exit] = " +_("Cancel") +"              [Ok] =" +_("Save"))
		CamCheckStop()

		self.onChangedEntry = [ ]
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
		self.createSetup()

		self["actions"] = ActionMap(["SetupActions", 'ColorActions'],
		{
			"ok": self.keySave,
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keySave,
			"menu": self.keyCancel,
		}, -2)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def createSetup(self):
		self.editListEntry = None
		self.list = []
		self.list.append(getConfigListEntry(_("Show CCcamInfo in Extensions Menu"), config.cccaminfo.showInExtensions))
		self.list.append(getConfigListEntry(_("Show OscamInfo in Extensions Menu"), config.oscaminfo.showInExtensions))
		self.list.append(getConfigListEntry(_("Frozen Cam Check"), config.plugins.extraspanel_frozencheck.list))
		
		self["config"].list = self.list
		self["config"].setList(self.list)

	def selectionChanged(self):
		self["status"].setText(self["config"].getCurrent()[0])

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()
		self.selectionChanged()
		self.createSetup()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def getCurrentDescription(self):
		return self["config"].getCurrent() and len(self["config"].getCurrent()) > 2 and self["config"].getCurrent()[2] or ""

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary
	
	def saveAll(self):
		if config.softcam.camstartMode.getValue() == "0":
			if os.path.exists("/etc/rc2.d/S20softcam.cam1"):
				print"Delete Symbolink link"
				self.container = eConsoleAppContainer()
				self.container.execute('update-rc.d -f softcam.cam1 defaults')
			if os.path.exists("/etc/init.d/softcam.cam1"):
				print"Delete softcam init script cam1"
				os.system("rm /etc/init.d/softcam.cam1")
				
			if os.path.exists("/etc/rc2.d/S20softcam.cam2"):
				print"Delete Symbolink link"
				self.container = eConsoleAppContainer()
				self.container.execute('update-rc.d -f softcam.cam2 defaults')
			if os.path.exists("/etc/init.d/softcam.cam2"):
				print"Delete softcam init script cam2"
				os.system("rm /etc/init.d/softcam.cam2")
			
		for x in self["config"].list:
			x[1].save()
		configfile.save()

	def keySave(self):
		self.saveAll()
		self.doClose()

	def cancelConfirm(self, result):
		if not result:
			return
		for x in self["config"].list:
			x[1].cancel()
		self.doClose()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"))
		else:
			self.doClose()

	def doClose(self):
		if not config.plugins.extraspanel_frozencheck.list.getValue() == '0':
			CamCheck()
		self.close()

class Info(Screen):
	def __init__(self, session, info):
		self.service = None
		Screen.__init__(self, session)

		self.skin = INFO_SKIN

		self["label2"] = Label("INFO")
		self["label1"] =  ScrollLabel()
		if info == "InfoPanel":
			self.InfoPanel()
		if info == "Sytem_info":
			self.Sytem_info()
		elif info == "Default":
			self.Default()
		elif info == "FreeSpace":
			self.FreeSpace()
		elif info == "Mounts":
			self.Mounts()
		elif info == "Network":
			self.Network()
		elif info == "Kernel":
			self.Kernel()
		elif info == "Free":
			self.Free()
		elif info == "Cpu":
			self.Cpu()
		elif info == "Top":
			self.Top()
		elif info == "MemInfo":
			self.MemInfo()
		elif info == "Module":
			self.Module()
		elif info == "Mtd":
			self.Mtd()
		elif info == "Partitions":
			self.Partitions()
		elif info == "Swap":
			self.Swap()

		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions"],
		{
			"cancel": self.Exit,
			"ok": self.ok,
			"up": self.Up,
			"down": self.Down,
		}, -1)

	def Exit(self):
		self.close()

	def ok(self):
		self.close()

	def Down(self):
		self["label1"].pageDown()

	def Up(self):
		self["label1"].pageUp()

	def InfoPanel(self):
		try:
			self["label2"].setText("INFO")
			info1 = self.Do_cmd("cat", "/etc/motd", None)
			if info1.find('wElc0me') > -1:
				info1 = info1[info1.find('wElc0me'):len(info1)] + "\n"
				info1 = info1.replace('|','')
			else:
				info1 = info1[info1.find('INFO'):len(info1)] + "\n"
			info2 = self.Do_cmd("cat", "/etc/image-version", None)
			info3 = self.Do_cut(info1 + info2)
			self["label1"].setText(info3)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Sytem_info(self):
		try:
			self["label2"].setText(_("Image Info"))
			info1 = self.Do_cmd("cat", "/etc/version", None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Default(self):

		try:
			self["label2"].setText(_("Default"))
			now = datetime.now()
			info1 = 'Date = ' + now.strftime("%d-%B-%Y") + "\n"
			info2 = 'Time = ' + now.strftime("%H:%M:%S") + "\n"
			info3 = self.Do_cmd("uptime", None, None)
			tmp = info3.split(",")
			info3 = 'Uptime = ' + tmp[0].lstrip() + "\n"
			info4 = self.Do_cmd("cat", "/etc/image-version", " | head -n 1")
			info4 = info4[9:]
			info4 = 'Boxtype = ' + info4 + "\n"
			info5 = 'Load = ' + self.Do_cmd("cat", "/proc/loadavg", None)
			info6 = self.Do_cut(info1 + info2 + info3 + info4 + info5)
			self["label1"].setText(info6)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def FreeSpace(self):
		try:
			self["label2"].setText(_("FreeSpace"))
			info1 = self.Do_cmd("df", None, "-h")
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Mounts(self):
		try:
			self["label2"].setText(_("Mounts"))
			info1 = self.Do_cmd("mount", None, None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Network(self):
		try:
			self["label2"].setText(_("Network"))
			info1 = self.Do_cmd("ifconfig", None, None) + '\n'
			info2 = self.Do_cmd("route", None, "-n")
			info3 = self.Do_cut(info1 + info2)
			self["label1"].setText(info3)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Kernel(self):
		try:
			self["label2"].setText(_("Kernel"))
			info0 = self.Do_cmd("cat", "/proc/version", None)
			info = info0.split('(')
			info1 = "Name = " + info[0] + "\n"
			info2 =  "Owner = " + info[1].replace(')','') + "\n"
			info3 =  "Mainimage = " + info[2][0:info[2].find(')')] + "\n"
			info4 = "Date = " + info[3][info[3].find('SMP')+4:len(info[3])]
			info5 = self.Do_cut(info1 + info2 + info3 + info4)
			self["label1"].setText(info5)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Free(self):
		try:
			self["label2"].setText(_("Ram"))
			info1 = self.Do_cmd("free", None, None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Cpu(self):
		try:
			self["label2"].setText(_("Cpu"))
			info1 = self.Do_cmd("cat", "/proc/cpuinfo", None, " | sed 's/\t\t/\t/'")
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Top(self):
		try:
			self["label2"].setText(_("Top"))
			info1 = self.Do_cmd("top", None, "-b -n1")
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def MemInfo(self):
		try:
			self["label2"].setText(_("MemInfo"))
			info1 = self.Do_cmd("cat", "/proc/meminfo", None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Module(self):
		try:
			self["label2"].setText(_("Module"))
			info1 = self.Do_cmd("cat", "/proc/modules", None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Mtd(self):
		try:
			self["label2"].setText(_("Mtd"))
			info1 = self.Do_cmd("cat", "/proc/mtd", None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Partitions(self):
		try:
			self["label2"].setText(_("Partitions"))
			info1 = self.Do_cmd("cat", "/proc/partitions", None)
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occured"))

	def Swap(self):
		try:
			self["label2"].setText(_("Swap"))
			info0 = self.Do_cmd("cat", "/proc/swaps", None, " | sed 's/\t/ /g; s/[ ]* / /g'")
			info0 = info0.split("\n");
			info1 = ""
			for l in info0[1:]:
				l1 = l.split(" ")
				info1 = info1 + "Name: " + l1[0] + '\n'
				info1 = info1 + "Type: " + l1[1] + '\n'
				info1 = info1 + "Size: " + l1[2] + '\n'
				info1 = info1 + "Used: " + l1[3] + '\n'
				info1 = info1 + "Prio: " + l1[4] + '\n\n'
			if info1[-1:] == '\n': info1 = info1[:-1]
			if info1[-1:] == '\n': info1 = info1[:-1]
			info1 = self.Do_cut(info1)
			self["label1"].setText(info1)
		except:
			self["label1"].setText(_("an internal error has occured"))


	def Do_find(self, text, search):
		text = text + ' '
		ret = ""
		pos = text.find(search)
		pos1 = text.find(" ", pos)
		if pos > -1:
			ret = text[pos + len(search):pos1]
		return ret

	def Do_cut(self, text):
		text1 = text.split("\n")
		text = ""
		for line in text1:
			text = text + line[:95] + "\n"
		if text[-1:] == '\n': text = text[:-1]
		return text

	def Do_cmd(self, cmd , file, arg , pipe = ""):
		try:
			if file != None:
				if os.path.exists(file) is True:
					o = command(cmd + ' ' + file + pipe, 0)
				else:
					o = "File not found: \n" + file
			else:
				if arg == None:
					o = command(cmd, 0)
				else:
					o = command(cmd + ' ' + arg, 0)
			return o
		except:
			o = ''
			return o
