from . import _
from Screens.Screen import Screen
from enigma import eTimer
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ConfigList import ConfigListScreen
from Components.config import getConfigListEntry, config, ConfigSelection, NoSave
from Components.Sources.List import List
from Components.Console import Console
from Components.Sources.StaticText import StaticText
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Plugins.Plugin import PluginDescriptor
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists
from os import system, rename, path, mkdir, remove, chmod
import fcntl
import os
from time import sleep
from re import search
import fstabViewer

device2 = ''

class DevicesMountPanel(Screen):
	skin = """
	<screen position="center,center" size="680,462" title="Mount Manager">
		<ePixmap pixmap="skin_default/buttons/red.png" position="40,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="190,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="340,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="490,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/key_menu.png" position="10,435" size="35,25" alphatest="on" />
		<widget name="key_red" position="40,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="190,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="key_yellow" position="340,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget name="key_blue" position="490,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		<widget name="key_menu" position="50,435" zPosition="1" size="250,21" font="Regular;19" halign="center" valign="center" foregroundColor="#00ffc000" transparent="1" />
		<widget source="list" render="Listbox" position="10,50" size="660,340" scrollbarMode="showOnDemand" >
			<convert type="TemplatedMultiContent">
				{"template": [
				 MultiContentEntryText(pos = (90, 0), size = (480, 30), color = 0x0058bcff, color_sel = 0x00ffc000, font=0, text = 0),
				 MultiContentEntryText(pos = (110, 30), size = (600, 50), font=1, flags = RT_VALIGN_TOP, text = 1),
				  MultiContentEntryText(pos = (580, 0), size = (80, 18), font=2,color = 0x00999999, color_sel = 0x00999999, flags = RT_VALIGN_CENTER, text = 3),
				 MultiContentEntryPixmapAlphaBlend(pos = (0, 0), size = (80, 80), png = 2),
				],
				"fonts": [gFont("Regular", 23),gFont("Regular", 19),gFont("Regular", 17)],
				"itemHeight": 85
				}
			</convert>
		</widget>
		<widget name="lab1" zPosition="2" position="30,90" size="600,50" font="Regular;22" halign="center" transparent="1"/>
	</screen>"""

	def __init__(self, session):
		self.setup_title = _("Mount Manager - edit label/fstab")
		Screen.__init__(self, session)
		self['key_red'] = Label(" ")
		self['key_green'] = Label()
		self['key_yellow'] = Label(_("Unmount"))
		self['key_blue'] = Label(_("Mount"))
		self['key_menu'] = Label(_("Setup Mounts"))
		self['lab1'] = Label()
		self.onChangedEntry = [ ]
		self.list = []
		self.mbox = None
		self.Console = None
		self['list'] = List(self.list)
		self["list"].onSelectionChanged.append(self.selectionChanged)
		self['actions'] = ActionMap(['WizardActions', 'ColorActions', "MenuActions"], {'back': self.close, 'red': self.saveMypoints, 'yellow': self.Unmount, 'blue': self.Mount, "menu": self.SetupMounts})
		self.activityTimer = eTimer()
		self.activityTimer.timeout.get().append(self.updateList2)
		self.updateList()
		self.setTitle(self.setup_title)

	def createSummary(self):
		return DevicesMountPanelSummary

	def setMainTitle(self):
		self.setTitle(self.setup_title)

	def selectionChanged(self):
		self.setMainTitle()
		self["key_red"].setText(" ")
		if len(self.list) == 0:
			return
		self.sel = self['list'].getCurrent()
		for line in self.sel:
			try:
				line = line.strip()
				#if line.find('Mount') >= 0:
				if _('Mount: ') in line:
					if line.find('/media/hdd') < 0:
						self["key_red"].setText(_("Use as HDD"))
			except:
				pass
		if self.sel:
			try:
				name = str(self.sel[0])
				desc = str(self.sel[1].replace('\t','  '))
			except:
				name = ""
				desc = ""
		else:
			name = ""
			desc = ""
		for cb in self.onChangedEntry:
			cb(name, desc)
	def updateList(self, result = None, retval = None, extra_args = None):
		scanning = _("Wait please while scanning for devices...")
		self['lab1'].setText(scanning)
		self.activityTimer.start(500)

	def updateList2(self):
		self.activityTimer.stop()
		self.list = []
		list2 = []
		try:
			f = open('/proc/partitions', 'r')
			fd = open('/proc/mounts', 'r')
			mnt = fd.readlines()
			fd.close()
		except:
			self['list'].list = self.list
			self['lab1'].hide()
			self.selectionChanged()
			return
		for line in f.readlines():
			mount_list =[]
			parts = line.strip().split()
			if not parts:
				continue
			device = parts[3]
			mmc = False
			if device and device == 'mmcblk0p1':
				mmc = True
			if not mmc and not search('sd[a-z][1-9]',device):
				continue
			if device in list2:
				continue
			for x in mnt:
				if x.find(device) != -1 and x not in mount_list:
					parts = x.strip().split()
					d1 = parts[1]
					mount_list.append(d1) 
			self.buildMy_rec(device, mount_list)
			list2.append(device)
		f.close()
		self['list'].list = self.list
		self['lab1'].hide()
		self.selectionChanged()

	def buildMy_rec(self, device, moremount = []):
		global device2
		device2 = ''
		try:
			if device.find('1') > 0:
				device2 = device.replace('1', '')
		except:
			device2 = ''
		try:
			if device.find('2') > 0:
				device2 = device.replace('2', '')
		except:
			device2 = ''
		try:
			if device.find('3') > 0:
				device2 = device.replace('3', '')
		except:
			device2 = ''
		try:
			if device.find('4') > 0:
				device2 = device.replace('4', '')
		except:
			device2 = ''
		try:
			if device.find('5') > 0:
				device2 = device.replace('5', '')
		except:
			device2 = ''
		try:
			if device.find('6') > 0:
				device2 = device.replace('6', '')
		except:
			device2 = ''
		try:
			if device.find('7') > 0:
				device2 = device.replace('7', '')
		except:
			device2 = ''
		try:
			if device.find('8') > 0:
				device2 = device.replace('8', '')
		except:
			device2 = ''
		try:
			if device.find('9') > 0:
				device2 = device.replace('9', '')
		except:
			device2 = ''
		try:
			if device == 'mmcblk0p1':
				device2 = 'mmcblk0'
		except:
			device2 = ''
		try:
			devicetype = path.realpath('/sys/block/' + device2 + '/device')
		except:
			devicetype = ''
		d2 = device
		model = "-?-"
		name = "USB: "
		if devicetype.find('sdhci') != -1:
			name = _("MMC: ")
			try:
				model = file('/sys/block/' + device2 + '/device/name').read()
				model = str(model).replace('\n', '')
			except:
				pass
			mypixmap = '/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/dev_mmc.png'
		else:
			mypixmap = '/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/dev_usb.png'
			try:
				model = file('/sys/block/' + device2 + '/device/model').read()
				model = str(model).replace('\n', '')
			except:
				pass
		des = ''
		if devicetype.find('/devices/pci') != -1 or devicetype.find('/devices/platform/strict-ahci') != -1:
			name = _("HARD DISK: ")
			mypixmap = '/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/dev_hdd.png'
		fullname = name + model
		self.Console = Console()
		self.Console.ePopen("sfdisk -l /dev/sd? | grep swap | awk '{print $(NF-9)}' >/tmp/devices.tmp")
		sleep(0.5)
		try:
			f = open('/tmp/devices.tmp', 'r')
			swapdevices = f.read()
			f.close()
		except:
			swapdevices = ''
		if path.exists('/tmp/devices.tmp'):
			remove('/tmp/devices.tmp')
		swapdevices = swapdevices.replace('\n','')
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
					d1 = _("None")
					dtype = 'swap'
					rw = _("None")
					break
					continue
				else:
					d1 = _("None")
					dtype = _("unavailable")
					rw = _("None")
		f.close()
		partition = False
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			if line.find(device) != -1:
				parts = line.strip().split()
				size = int(parts[2])
				if (((float(size) / 1024) / 1024) / 1024) > 1:
					des = _("Size: ") + str(round((((float(size) / 1024) / 1024) / 1024),2)) + " " + _("TB")
				elif ((size / 1024) / 1024) > 1:
					capacity = (size / 1024) / 1024
					des = _("Size: ") + str(capacity) + " " + _("GB")
					if capacity > 256 and name == _("USB: "):
						mypixmap = '/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/dev_usb_drive.png'
						partition = True
				else:
					des = _("Size: ") + str(size / 1024) + " " + _("MB")
			else:
				try:
					size = file('/sys/block/' + device2 + '/' + device + '/size').read()
					size = str(size).replace('\n', '')
					size = int(size)
				except:
					size = 0
				if ((((float(size) / 2) / 1024) / 1024) / 1024) > 1:
					des = _("Size: ") + str(round(((((float(size) / 2) / 1024) / 1024) / 1024),2)) + _("TB")
				elif (((size / 2) / 1024) / 1024) > 1:
					capacity = ((size / 2) / 1024) / 1024
					des = _("Size: ") + str(capacity) + " " + _("GB")
					if capacity > 256 and name == _("USB: "):
						mypixmap = '/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/dev_usb_drive.png'
						partition = True
				else:
					des = _("Size: ") + str((size / 2) / 1024) + " " + _("MB")
		f.close()
		if des != '':
			if rw.startswith('rw'):
				rw = ' R/W'
			elif rw.startswith('ro'):
				rw = ' R/O'
			else:
				rw = ""
			prev_des = des
			des += '\t' + _("Mount: ") + d1 + '\n' + _("Device: ") + '/dev/' + device + '\t' + _("Type: ") + dtype + rw
			png = LoadPixmap(mypixmap)
			extmount = False
			num_mount = len(moremount)
			extmount = num_mount > 1 and _("%s points") % str(num_mount) or ""
			res = (fullname, des, png, extmount)
			self.list.append(res)
			if num_mount > 1:
				for mnt in moremount:
					if str(mnt) != d1:
						prev_des += '\t' + _("Mount: ") + str(mnt) + '\n' + _("Device: ") + '/dev/' + device + '\t' + _("Type: ") + dtype + rw
						res = (fullname, prev_des, png, extmount)
						if res not in self.list:
							self.list.append(res)

	def SetupMounts(self):
		self.session.openWithCallback(self.updateList, DeviceMountPanelConf)

	def Mount(self):
		if len(self['list'].list) < 1: return
		sel = self['list'].getCurrent()
		if sel:
			des = sel[1]
			des = des.replace('\n', '\t')
			parts = des.strip().split('\t')
			mountp = parts[1].replace(_("Mount: "), '')
			device = parts[2].replace(_("Device: "), '')
			moremount = sel[3]
			adv_title = moremount != "" and _("Warning, this device is used for more than one mount point!\n") or ""
			if device != '':
				devicemount = device[-5:]
				curdir = '/media%s' % (devicemount)
				mountlist = [
				(_("Mount current device from the fstab"), self.MountCur3),
				(_("Mount current device to %s") % (curdir), self.MountCur2),
				(_("Mount all device from the fstab"), self.MountCur1),
				]
				self.session.openWithCallback(
				self.menuCallback,
				ChoiceBox,
				list = mountlist,
				title= adv_title + _("Select mount action for %s:") % device,
				)

	def menuCallback(self, ret = None):
		ret and ret[1]()

	def MountCur3(self):
		sel = self['list'].getCurrent()
		if sel:
			parts = sel[1].split()
			self.device = parts[5]
			self.mountp = parts[3]
			des = sel[1]
			des = des.replace('\n', '\t')
			parts = des.strip().split('\t')
			device = parts[2].replace(_("Device: "), '')
			try:
				f = open('/proc/mounts', 'r')
			except IOError:
				return
			for line in f.readlines():
				if line.find(device) != -1:
					self.session.open(MessageBox, _("The device is already mounted!"), MessageBox.TYPE_INFO, timeout=5)
					f.close()
					return
			f.close()
			self.mbox = self.session.open(MessageBox, _("Please wait..."), MessageBox.TYPE_INFO)
			system('mount ' + device)
			self.Console = Console()
			self.Console.ePopen("/sbin/blkid | grep " + self.device, self.cur_in_fstab, [self.device, self.mountp])

	def MountCur1(self):
		if len(self['list'].list) < 1: return
		system('mount -a')
		self.updateList()

	def MountCur2(self):
		sel = self['list'].getCurrent()
		if sel:
			des = sel[1]
			des = des.replace('\n', '\t')
			parts = des.strip().split('\t')
			device = parts[2].replace(_("Device: "), '')
			try:
				f = open('/proc/mounts', 'r')
			except IOError:
				return
			for line in f.readlines():
				if line.find(device) != -1:
					f.close()
					self.session.open(MessageBox, _("The device is already mounted!"), MessageBox.TYPE_INFO, timeout=5)
					return
			f.close()
			if device != '':
				devicemount = device[-5:]
				mountdir = '/media/%s' % (devicemount)
				if not path.exists(mountdir):
					mkdir(mountdir, 0755)
				system ('mount ' + device + ' /media/%s' % (devicemount))
				mountok = False
				f = open('/proc/mounts', 'r')
				for line in f.readlines():
					if line.find(device) != -1:
						mountok = True
				f.close()
				if not mountok:
					self.session.open(MessageBox, _("Mount failed!"), MessageBox.TYPE_ERROR, timeout=5)
				self.updateList()

	def cur_in_fstab(self, result = None, retval = None, extra_args = None):
		self.device = extra_args[0]
		self.mountp = extra_args[1]
		self.device_uuid_tmp = result.split('UUID=')
		if str(self.device_uuid_tmp) != "['']":
			try:
				self.device_uuid_tmp = self.device_uuid_tmp[1].replace('TYPE="ext2"','').replace('TYPE="ext3"','').replace('TYPE="ext4"','').replace('TYPE="ntfs"','').replace('TYPE="exfat"','').replace('TYPE="vfat"','').replace('"','')
				self.device_uuid_tmp = self.device_uuid_tmp.replace('\n',"")
				self.device_uuid = 'UUID=' + self.device_uuid_tmp
				system ('mount ' + self.device_uuid)
				mountok = False
				f = open('/proc/mounts', 'r')
				for line in f.readlines():
					if line.find(self.device) != -1:
						mountok = True
				f.close()
				if not mountok:
					self.session.open(MessageBox, _("Mount current device failed!\nMaybe this device is not spelled out in the fstab?"), MessageBox.TYPE_ERROR, timeout=8)
			except:
				pass
		if self.mbox:
			self.mbox.close()
		self.updateList()

	def Unmount(self):
		if len(self['list'].list) < 1: return
		sel = self['list'].getCurrent()
		if sel:
			des = sel[1]
			des = des.replace('\n', '\t')
			parts = des.strip().split('\t')
			mountp = parts[1].replace(_("Mount: "), '')
			device = parts[2].replace(_("Device: "), '')
			print mountp
			if mountp == _("None"): return
			message = _('Really unmount ') + device + _(" from ") +  mountp + " ?"
			self.session.openWithCallback(self.UnmountAnswer, MessageBox, message, MessageBox.TYPE_YESNO)

	def UnmountAnswer(self, answer):
		if answer:
			sel = self['list'].getCurrent()
			if sel:
				des = sel[1]
				des = des.replace('\n', '\t')
				parts = des.strip().split('\t')
				mountp = parts[1].replace(_("Mount: "), '')
				device = parts[2].replace(_("Device: "), '')
				moremount = sel[3]
				if mountp != _("None"):
					system('umount ' + mountp)
				if moremount == "":
					system('umount ' + device)
				try:
					mounts = open("/proc/mounts")
				except IOError:
					return
				mountcheck = mounts.readlines()
				mounts.close()
				for line in mountcheck:
					#if moremount == "":
					#	parts = line.strip().split(" ")
					#	if path.realpath(parts[0]).startswith(device):
					#		self.session.open(MessageBox, _("Can't unmount partiton, make sure it is not being used for swap or record/timeshift paths!"), MessageBox.TYPE_ERROR, timeout = 6, close_on_any_key = True)
					if mountp in line and device in line:
						parts = line.strip().split(" ")
						if parts[1] == mountp:
							self.session.open(MessageBox, _("Can't unmount partiton, make sure it is not being used for swap or record/timeshift paths!"), MessageBox.TYPE_ERROR, timeout = 5, close_on_any_key = True)
							break
				self.updateList()

	def saveMypoints(self):
		if len(self['list'].list) < 1: return
		sel = self['list'].getCurrent()
		if sel:
			des = sel[1]
			des = des.replace('\n', '\t')
			parts = des.strip().split('\t')
			device = parts[2].replace(_("Device: "), '')
			moremount = sel[3]
			adv_title = moremount != "" and _("Warning, this device is used for more than one mount point!\n") or ""
			message = adv_title + _("Really use and mount %s as HDD ?") % device
			self.session.openWithCallback(self.saveMypointAnswer, MessageBox, message, MessageBox.TYPE_YESNO)

	def saveMypointAnswer(self, answer):
		if answer:
			sel = self['list'].getCurrent()
			if sel:
				des = sel[1]
				des = des.replace('\n', '\t')
				parts = des.strip().split('\t')
				self.mountp = parts[1].replace(_("Mount: "), '')
				self.device = parts[2].replace(_("Device: "), '')
				if self.mountp.find('/media/hdd') < 0:
					pass
				else:
					self.session.open(MessageBox, _("This Device is already mounted as HDD."), MessageBox.TYPE_INFO, timeout = 6, close_on_any_key = True)
					return
				system('[ -e /media/hdd/swapfile ] && swapoff /media/hdd/swapfile')
				#system('[ -e /etc/init.d/transmissiond ] && /etc/init.d/transmissiond stop')
				system('umount /media/hdd')
				try:
					f = open('/proc/mounts', 'r')
				except IOError:
					return
				for line in f.readlines():
					if '/media/hdd' in line:
						f.close()
						self.session.open(MessageBox, _("Cannot unmount from the previous device from /media/hdd.\nA record in progress, timeshift or some external tools (like samba, nfsd,transmission and etc) may cause this problem.\nPlease stop this actions/applications and try again!"), MessageBox.TYPE_ERROR)
						return
					else:
						pass
				f.close()
				if self.mountp.find('/media/hdd') < 0:
					if self.mountp != _("None"):
						system('umount ' + self.mountp)
					system('umount ' + self.device)
					self.Console.ePopen("/sbin/blkid | grep " + self.device, self.add_fstab, [self.device, self.mountp])

	def add_fstab(self, result = None, retval = None, extra_args = None):
		self.device = extra_args[0]
		self.mountp = extra_args[1]
		self.device_uuid_tmp = result.split('UUID=')
		if str(self.device_uuid_tmp) != "['']":
			self.device_uuid_tmp = self.device_uuid_tmp[1].replace('TYPE="ext2"','').replace('TYPE="ext3"','').replace('TYPE="ext4"','').replace('TYPE="ntfs"','').replace('TYPE="exfat"','').replace('TYPE="vfat"','').replace('TYPE="xfs"','').replace('"','')
			self.device_uuid_tmp = self.device_uuid_tmp.replace('\n',"")
			self.device_uuid = 'UUID=' + self.device_uuid_tmp
			if not path.exists(self.mountp):
				mkdir(self.mountp, 0755)
			flashexpander = None
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Flashexpander/plugin.pyo") and fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Flashexpander/flashexpander.pyo"):
				try:
					f = open("/etc/fstab", 'r')
					for line in f.readlines():
						if line.find('/usr') > -1 and line.startswith(self.device_uuid):
							flashexpander = line
					f.close()
				except:
					pass
			file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if '/media/hdd' not in l])
			rename('/etc/fstab.tmp','/etc/fstab')
			file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if self.device not in l])
			rename('/etc/fstab.tmp','/etc/fstab')
			file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if self.device_uuid not in l])
			rename('/etc/fstab.tmp','/etc/fstab')
			out = open('/etc/fstab', 'a')
			line = self.device_uuid + ' /media/hdd auto defaults 0 0\n'
			if flashexpander is not None:
				line += flashexpander
			out.write(line)
			out.close()
			self.Console.ePopen('mount /media/hdd', self.updateList)

	def restBo(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 2)
		else:
			self.updateList()

class DeviceMountPanelConf(Screen, ConfigListScreen):
	skin = """
	<screen position="center,center" size="730,300" title="Setup Mounts">
		<ePixmap pixmap="skin_default/buttons/red.png" position="15,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="165,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="315,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="490,0" size="140,40" alphatest="on" />
		<widget name="key_red" position="15,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="165,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="key_yellow" position="315,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget name="key_blue" position="490,0" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		<widget name="config" position="0,60" size="730,215" scrollbarMode="showOnDemand"/>
		<widget name="Linconn" position="30,375" size="680,40" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313"/>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		Screen.setTitle(self, _("Setup Mounts"))
		self['key_green'] = Label(_("Save mount in fstab"))
		self['key_red'] = Label(_("Label for device"))
		self['key_yellow'] = Label(_("Edit fstab"))
		self['key_blue'] = Label(_("Install / Info"))
		self['Linconn'] = Label(_("Wait please while scanning your box devices..."))
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'green': self.saveMypoints, 'red': self.editLabel, 'yellow': self.editFstab, 'blue': self.systemInfo, 'back': self.close})
		self.checkMount = False
		self.Checktimer = eTimer()
		self.Checktimer.callback.append(self.check_cur_Umount)
		self.label_device = ""
		self.updateList2()

	def updateList2(self):
		self.list = []
		list2 = []
		self.Console = Console()
		self.Console.ePopen("sfdisk -l /dev/sd? | grep swap | awk '{print $(NF-9)}' >/tmp/devices.tmp")
		sleep(0.5)
		try:
			f = open('/tmp/devices.tmp', 'r')
			swapdevices = f.read()
			f.close()
		except:
			swapdevices = ''
		if path.exists('/tmp/devices.tmp'):
			remove('/tmp/devices.tmp')
		swapdevices = swapdevices.replace('\n','')
		swapdevices = swapdevices.split('/')
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			parts = line.strip().split()
			if not parts:
				continue
			device = parts[3]
			mmc = False
			if device and device == 'mmcblk0p1':
				mmc = True
			if not mmc and not search('sd[a-z][1-9]',device):
				continue
			if device in list2:
				continue
			if device in swapdevices:
				continue
			self.buildMy_rec(device)
			list2.append(device)
		f.close()
		self['config'].list = self.list
		self['config'].l.setList(self.list)
		self['Linconn'].hide()

	def buildMy_rec(self, device):
		global device2
		device2 = ''
		try:
			if device.find('1') > 0:
				device2 = device.replace('1', '')
		except:
			device2 = ''
		try:
			if device.find('2') > 0:
				device2 = device.replace('2', '')
		except:
			device2 = ''
		try:
			if device.find('3') > 0:
				device2 = device.replace('3', '')
		except:
			device2 = ''
		try:
			if device.find('4') > 0:
				device2 = device.replace('4', '')
		except:
			device2 = ''
		try:
			if device.find('5') > 0:
				device2 = device.replace('5', '')
		except:
			device2 = ''
		try:
			if device.find('6') > 0:
				device2 = device.replace('6', '')
		except:
			device2 = ''
		try:
			if device.find('7') > 0:
				device2 = device.replace('7', '')
		except:
			device2 = ''
		try:
			if device.find('8') > 0:
				device2 = device.replace('8', '')
		except:
			device2 = ''
		try:
			if device.find('9') > 0:
				device2 = device.replace('9', '')
		except:
			device2 = ''
		try:
			if device =='mmcblk0p1':
				device2 = 'mmcblk0'
		except:
			device2 = ''
		try:
			devicetype = path.realpath('/sys/block/' + device2 + '/device')
		except:
			devicetype = ''
		d2 = device
		model = '-?-'
		name = "USB: "
		if 'sdhci' in devicetype:
			name = "MMC: "
			try:
				model = file('/sys/block/' + device2 + '/device/name').read()
			except:
				pass
			model = str(model).replace('\n', '')
		else:
			try:
				model = file('/sys/block/' + device2 + '/device/model').read()
			except:
				pass
			model = str(model).replace('\n', '')
		des = ''
		if devicetype.find('/devices/pci') != -1 or devicetype.find('/devices/platform/strict-ahci') != -1:
			name = _("HARD DISK: ")
		name = name + model
		f = open('/proc/mounts', 'r')
		for line in f.readlines():
			if line.find(device) != -1:
				parts = line.strip().split()
				d1 = parts[1]
				dtype = parts[2]
				break
				continue
			else:
				d1 = _("None")
				dtype = _("unavailable")
		f.close()
		f = open('/proc/partitions', 'r')
		for line in f.readlines():
			if line.find(device) != -1:
				parts = line.strip().split()
				size = int(parts[2])
				if (((float(size) / 1024) / 1024) / 1024) > 1:
					des = _("Size: ") + str(round((((float(size) / 1024) / 1024) / 1024),2)) + " " + _("TB")
				elif ((size / 1024) / 1024) > 1:
					des = _("Size: ") + str((size / 1024) / 1024) + " " + _("GB")
				else:
					des = _("Size: ") + str(size / 1024) + " " + _("MB")
			else:
				try:
					size = file('/sys/block/' + device2 + '/' + device + '/size').read()
					size = str(size).replace('\n', '')
					size = int(size)
				except:
					size = 0
				if ((((float(size) / 2) / 1024) / 1024) / 1024) > 1:
					des = _("Size: ") + str(round(((((float(size) / 2) / 1024) / 1024) / 1024),2)) + " " + _("TB")
				elif (((size / 2) / 1024) / 1024) > 1:
					des = _("Size: ") + str(((size / 2) / 1024) / 1024) + " " + _("GB")
				else:
					des = _("Size: ") + str((size / 2) / 1024) + " " + _("MB")
		f.close()
		choices = [('/media/' + device, '/media/' + device), ('/media/hdd', '/media/hdd'), ('/media/hdd2', '/media/hdd2'), ('/media/hdd3', '/media/hdd3'), ('/media/usb_hdd', '/media/usb_hdd'), ('/media/usb', '/media/usb'), ('/media/usb2', '/media/usb2'), ('/media/usb3', '/media/usb3')]
		if 'MMC' in name:
			choices.append(('/media/mmc', '/media/mmc'))
		item = NoSave(ConfigSelection(default='/media/' + device, choices=choices))
		if dtype == 'Linux':
			dtype = 'ext3'
		else:
			dtype = 'auto'
		item.value = d1.strip()
		text = name + ' ' + des + ' /dev/' + device
		res = getConfigListEntry(text, item, device, dtype)
		if des != '' and self.list.append(res):
			pass

	def editFstab(self):
		self.session.open(fstabViewer.fstabViewerScreen)

	def editLabel(self):
		self.label_device = ""
		sel = self['config'].getCurrent()
		if sel and len(sel) > 2:
			des = sel[2]
			if des and des != "":
				des = des.replace('\n', '\t')
				device = '/dev/' + des
				if path.exists(device):
					self.label_device = device
					if path.exists('/sbin/tune2fs'):
						self.openEditLabelDevice(device)
					else:
						self.session.open(MessageBox, _("Please install tune2fs"), MessageBox.TYPE_INFO)

	def openEditLabelDevice(self, device=''):
		if device:
			title_text = _("Please enter label for %s:") % device
			self.session.openWithCallback(self.renameEntryCallback, VirtualKeyBoard, title=title_text, text='')

	def renameEntryCallback(self, answer):
		if answer is not None:
			edit_fstab = False
			if answer != "":
				edit_fstab = True
			ret = system("/sbin/tune2fs %s -L '%s'" % (self.label_device, answer))
			if ret == 0:
				if edit_fstab:
					self.Console = Console()
					self.Console.ePopen("/sbin/blkid | grep " + self.label_device, self.delCurrentUUID, [self.label_device])
				message = _("Device changes need a system restart to take effects.\nRestart your Box now?")
				ybox = self.session.openWithCallback(self.restartBox, MessageBox, message, MessageBox.TYPE_YESNO)
				ybox.setTitle(_("Restart Box..."))
			else:
				self.label_device = ""
				self.close()

	def delCurrentUUID(self, result = None, retval = None, extra_args = None):
		self.device = extra_args[0]
		if result and self.device in result:
			pass
		else:
			return
		self.device_uuid_tmp = result.split('UUID=')
		if str(self.device_uuid_tmp) != "['']":
			self.device_uuid_tmp = self.device_uuid_tmp[1].replace('TYPE="ext2"','').replace('TYPE="ext3"','').replace('TYPE="ext4"','').replace('TYPE="ntfs"','').replace('TYPE="exfat"','').replace('TYPE="vfat"','').replace('TYPE="xfs"','').replace('"','')
			self.device_uuid_tmp = self.device_uuid_tmp.replace('\n',"")
			self.device_uuid = 'UUID=' + self.device_uuid_tmp
			flashexpander = None
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Flashexpander/plugin.pyo") and fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Flashexpander/flashexpander.pyo"):
				try:
					f = open("/etc/fstab", 'r')
					for line in f.readlines():
						if line.find('/usr') > -1 and line.startswith(self.device_uuid):
							flashexpander = line
					f.close()
				except:
					pass
			file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if self.device not in l])
			rename('/etc/fstab.tmp','/etc/fstab')
			file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if self.device_uuid not in l])
			rename('/etc/fstab.tmp','/etc/fstab')
			if flashexpander is not None:
				out = open('/etc/fstab', 'a')
				line = flashexpander
				out.write(line)
				out.close()

	def systemInfo(self):
		mylist = [
		(_("mount"), self.action1),
		(_("df -h"), self.action2),
		(_("sfdisk -l"), self.action3),
		(_("blkid"), self.action4),
		(_("install ext2 kernel module"), self.action5),
		(_("install ext3 kernel module"), self.action6),
		(_("install filesystem utilities (e2fsprogs)"), self.action7),
		(_("install filesystem utilities (e2fsprogs-tune2fs)"), self.action8),
		(_("install linux utilities (fdisk)"), self.action9),
		(_("install linux utilities (util-linux-blkid)"), self.action10),
		]
		self.session.openWithCallback(
		self.menuCallback,
		ChoiceBox,
		list = mylist,
		title= _("Select system info or install module:"),
		)

	def action1(self):
		from Screens.Console import Console as myConsole
		self.session.open(myConsole,_("*****mount*****"),["mount"])

	def action2(self):
		from Screens.Console import Console as myConsole
		self.session.open(myConsole,_("*****df -h*****"),["df -h"])

	def action3(self):
		from Screens.Console import Console as myConsole
		self.session.open(myConsole,_("*****sfdisk -l*****"),["sfdisk -l"])
		
	def action4(self):
		from Screens.Console import Console as myConsole
		self.session.open(myConsole,_("*****blkid*****"),["blkid"])

	def action5(self):
		from Screens.Console import Console as myConsole
		self.session.open(myConsole,_("*****kernel-module-ext2*****"),["opkg install kernel-module-ext2"])

	def action6(self):
		from Screens.Console import Console as myConsole
		self.session.open(myConsole,_("*****kernel-module-ext3*****"),["opkg install kernel-module-ext3"])

	def action7(self):
		from Screens.Console import Console as myConsole
		self.session.open(myConsole,_("*****e2fsprogs*****"),["opkg install e2fsprogs"])

	def action8(self):
		from Screens.Console import Console as myConsole
		self.session.open(myConsole,_("*****e2fsprogs-tune2fs*****"),["opkg install e2fsprogs-tune2fs"])

	def action9(self):
		from Screens.Console import Console as myConsole
		self.session.open(myConsole,_("*****fdisk*****"),["opkg install util-linux-fdisk"])

	def action10(self):
		from Screens.Console import Console as myConsole
		self.session.open(myConsole,_("*****util-linux-blkid*****"),["opkg install util-linux-blkid"])

	def saveMypoints(self):
		if len(self['config'].list) < 1: return
		message = _("Really save in fstab mount by UUID:\n")
		val = []
		for x in self['config'].list:
			device = x[2]
			mountp = x[1].value
			if mountp not in val: 
				val.append((mountp))
			else:
				self.session.open(MessageBox, _("Error!\nThe same mount point!"), MessageBox.TYPE_ERROR, timeout=5)
				return
			message += '/dev/' + device + _(" as ") +  mountp + "\n"
		self.session.openWithCallback(self.saveMypointsAnswer, MessageBox, message, MessageBox.TYPE_YESNO)

	def saveMypointsAnswer(self, answer):
		if answer:
			self.Console = Console()
			system('[ -e /media/hdd/swapfile ] && swapoff /media/hdd/swapfile')
			#system('[ -e /etc/init.d/transmissiond ] && /etc/init.d/transmissiond stop')
			system('[ -e /media/usb/swapfile ] && swapoff /media/usb/swapfile')
			for x in self['config'].list:
				self.device = x[2]
				self.mountp = x[1].value
				self.type = x[3]
				self.Console.ePopen('umount -f /dev/%s 2>&1' % (self.device))
				self.Console.ePopen("/sbin/blkid | grep " + self.device, self.add_fstab, [self.device, self.mountp] )
				self.Checktimer.stop()
				self.Checktimer.start(2500, True)

	def check_cur_Umount(self):
		self.checkMount = False
		file_mounts = '/proc/mounts'
		if fileExists(file_mounts):
			fd = open(file_mounts,'r')
			lines_mount = fd.readlines()
			fd.close()
			for line in lines_mount:
				l = line.split(' ')
				if l[0][:7] == '/dev/sd' or l[0][:7] == 'mmcblk0p1':
					self.checkMount = True
		self.select_action()

	def select_action(self):
		if self.checkMount:
			self.checkMount = False
			message = _("Devices changes need a system restart to take effects.\nRestart your Box now?")
			ybox = self.session.openWithCallback(self.restartBox, MessageBox, message, MessageBox.TYPE_YESNO)
			ybox.setTitle(_("Restart Box..."))
		else:
			mylist = [
			(_("Mount all device from the fstab"), self.AllMount),
			(_("Restart your box"), self.answerRestart),
			(_("Exit"), self.answerExit),
			]
			self.session.openWithCallback(
			self.menuCallback,
			ChoiceBox,
			list = mylist,
			title= _("All device umount.Select action:"),
			)

	def answerRestart(self):
		self.restartBox(True)

	def answerExit(self):
		self.close()

	def menuCallback(self, ret = None):
		ret and ret[1]()

	def AllMount(self):
		system('mount -a')
		self.close()

	def add_fstab(self, result = None, retval = None, extra_args = None):
		self.device = extra_args[0]
		self.mountp = extra_args[1]
		self.device_uuid_tmp = result.split('UUID=')
		if str(self.device_uuid_tmp) != "['']":
			self.device_uuid_tmp = self.device_uuid_tmp[1].replace('TYPE="ext2"','').replace('TYPE="ext3"','').replace('TYPE="ext4"','').replace('TYPE="ntfs"','').replace('TYPE="exfat"','').replace('TYPE="vfat"','').replace('TYPE="xfs"','').replace('"','')
			self.device_uuid_tmp = self.device_uuid_tmp.replace('\n',"")
			self.device_uuid = 'UUID=' + self.device_uuid_tmp
			if not path.exists(self.mountp):
				mkdir(self.mountp, 0755)
			flashexpander = None
			if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Flashexpander/plugin.pyo") and fileExists("/usr/lib/enigma2/python/Plugins/Extensions/Flashexpander/flashexpander.pyo"):
				try:
					f = open("/etc/fstab", 'r')
					for line in f.readlines():
						if line.find('/usr') > -1 and line.startswith(self.device_uuid):
							flashexpander = line
					f.close()
				except:
					pass
			file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if self.device not in l])
			rename('/etc/fstab.tmp','/etc/fstab')
			file('/etc/fstab.tmp', 'w').writelines([l for l in file('/etc/fstab').readlines() if self.device_uuid not in l])
			rename('/etc/fstab.tmp','/etc/fstab')
			out = open('/etc/fstab', 'a')
			line = self.device_uuid + '' + self.mountp + ' auto defaults 0 0\n'
			if flashexpander is not None:
				line += flashexpander
			out.write(line)
			out.close()

	def restartBox(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 2)
		else:
			self.close()

class DevicesMountPanelSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent = parent)
		self["entry"] = StaticText("")
		self["desc"] = StaticText("")
		self.onShow.append(self.addWatcher)
		self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		self.parent.onChangedEntry.append(self.selectionChanged)
		self.parent.selectionChanged()

	def removeWatcher(self):
		self.parent.onChangedEntry.remove(self.selectionChanged)

	def selectionChanged(self, name, desc):
		self["entry"].text = name
		self["desc"].text = desc

def StartSetup(menuid, **kwargs):
	if menuid == "system":
		return [(_("Mount Manager"), OpenSetup, "mountpoints_setup", None)]
	else:
		return []

def OpenSetup(session, **kwargs):
	session.open(DevicesMountPanel)

def Plugins(**kwargs):
	return [PluginDescriptor(name = "Mount Manager", description = _("Manage you devices mountpoints"), where = PluginDescriptor.WHERE_MENU, fnc = StartSetup)]