#################################################################################
#         FULL BACKUP UYILITY FOR ENIGMA2, SUPPORTS THE MODELS OE-A 4.3         #
#                                                                               #
#                    MAKES A FULLBACK-UP READY FOR FLASHING.                    #
#                                                                               #
#################################################################################
from enigma import getEnigmaVersionString
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.SystemInfo import SystemInfo
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.About import about
from Components import Harddisk
from Components.ChoiceList import ChoiceList, ChoiceEntryComponent
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from time import time, strftime, localtime
from Tools.BoundFunction import boundFunction
from Tools.Multiboot import getImagelist, getCurrentImage, getCurrentImageMode, GetBoxName
import os
import commands
import datetime
from boxbranding import getMachineBrand, getMachineName, getDriverDate, getImageVersion, getImageBuild, getBrandOEM, getMachineBuild, getImageFolder, getMachineUBINIZE, getMachineMKUBIFS, getMachineMtdKernel, getMachineMtdRoot, getMachineKernelFile, getMachineRootFile, getImageFileSystem, getImageDistro, getImageVersion

VERSION = _('Version') + ' %s %s images' % (getImageVersion(), getImageDistro())


class ImageBackup(Screen):
	skin = """
	<screen name="Image Backup" position="center,center" size="750,900" flags="wfNoBorder" backgroundColor="transparent">
		<eLabel name="b" position="0,0" size="750,700" backgroundColor="#00ffffff" zPosition="-2" />
		<eLabel name="a" position="1,1" size="748,698" backgroundColor="#00000000" zPosition="-1" />
		<widget source="Title" render="Label" position="60,10" foregroundColor="#00ffffff" size="480,50" halign="left" font="Regular; 28" backgroundColor="#00000000" />
		<eLabel name="line" position="1,60" size="748,1" backgroundColor="#00ffffff" zPosition="1" />
		<eLabel name="line2" position="1,250" size="748,4" backgroundColor="#00ffffff" zPosition="1" />
		<widget name="config" position="2,280" size="730,380" halign="center" font="Regular; 22" backgroundColor="#00000000" foregroundColor="#00e5b243" />
		<widget source="description" render="Label" position="2,80" size="730,30" halign="center" font="Regular; 22" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="options" render="Label" position="2,130" size="730,60" halign="center" font="Regular; 22" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="key_red" render="Label" position="30,200" size="150,30" noWrap="1" zPosition="1" valign="center" font="Regular; 20" halign="left" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<widget source="key_green" render="Label" position="200,200" size="150,30" noWrap="1" zPosition="1" valign="center" font="Regular; 20" halign="left" backgroundColor="#00000000" foregroundColor="#00ffffff" />
		<eLabel position="20,200" size="6,40" backgroundColor="#00e61700" /> <!-- Should be a pixmap -->
		<eLabel position="190,200" size="6,40" backgroundColor="#0061e500" /> <!-- Should be a pixmap -->
	</screen>"""

	def __init__(self, session, args=0):
		Screen.__init__(self, session)
		self.title = _("Image Backup")
		self["key_red"] = StaticText(_("Cancel"))
		self["description"] = StaticText(_("Use the cursor keys to select an installed image and then Start button."))
		self["options"] = StaticText(_(" "))
		self["key_green"] = StaticText(_("Start"))
		self["config"] = ChoiceList(list=[ChoiceEntryComponent('', ((_("Retrieving image slots - Please wait...")), "Queued"))])
		imagedict = []
		self.getImageList = None

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "KeyboardInputActions", "MenuActions"],
		{
			"red": boundFunction(self.close, None),
			"green": self.start,
			"ok": self.start,
			"cancel": boundFunction(self.close, None),
			"up": self.keyUp,
			"down": self.keyDown,
			"left": self.keyLeft,
			"right": self.keyRight,
			"upRepeated": self.keyUp,
			"downRepeated": self.keyDown,
			"leftRepeated": self.keyLeft,
			"rightRepeated": self.keyRight,
			"menu": boundFunction(self.close, True),
		}, -1)
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.title)
		self.ImageList()

	def ImageList(self):
		imagedict = getImagelist()
		self.saveImageList = imagedict
		list = []
		currentimageslot = getCurrentImage() or 1
		print "[Image Backup] Current Image Slot %s, Imagelist %s" % (currentimageslot, imagedict)
		if imagedict:
			for x in sorted(imagedict.keys()):
				if imagedict[x]["imagename"] != _("Empty slot"):
					if x == 1 and currentimageslot == 1 and SystemInfo["canRecovery"]:
						list.append(ChoiceEntryComponent('', (_("slot%s - %s as USB Recovery") % (x, imagedict[x]["imagename"]), x, True)))
					list.append(ChoiceEntryComponent('', ((_("slot%s - %s (current image)") if x == currentimageslot else _("slot%s - %s")) % (x, imagedict[x]["imagename"]), x, False)))
		else:
			if SystemInfo["canRecovery"]:
				list.append(ChoiceEntryComponent('', (_("internal flash: %s %s as USB Recovery") % (getImageDistro(), getImageVersion()), "x", True)))
			list.append(ChoiceEntryComponent('', (_("internal flash:  %s %s ") % (getImageDistro(), getImageVersion()), "x", False)))
		self["config"].setList(list)

	def start(self):
		self.currentSelected = self["config"].l.getCurrentSelection()
		title = _("Please select a backup destination")
		choices = []
		retval = []
		if self.currentSelected[0][1] != "Queued":
			for media in ['/media/%s' % x for x in os.listdir('/media')] + (['/media/net/%s' % x for x in os.listdir('/media/net')] if os.path.isdir('/media/net') else []):
				if Harddisk.Freespace(media) > 300000:
					choices.append((_("Backup to destination: %s") % (media), self.currentSelected[0][1], media, self.currentSelected[0][2]))
			choices.append((_("No, do not backup an image"), False))
			self.session.openWithCallback(self.doFullBackup, ChoiceBox, title=title, list=choices)

	def selectionChanged(self):
		currentSelected = self["config"].l.getCurrentSelection()

	def keyLeft(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.selectionChanged()

	def keyRight(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.selectionChanged()

	def keyUp(self):
		self["config"].instance.moveSelection(self["config"].instance.moveUp)
		self.selectionChanged()

	def keyDown(self):
		self["config"].instance.moveSelection(self["config"].instance.moveDown)
		self.selectionChanged()

	def doFullBackup(self, answer):
		if answer is not None:
			if answer[1]:
				self.RECOVERY = answer[3]
				self.DIRECTORY = "%s/fullbackup" % answer[2]
				if not os.path.exists(self.DIRECTORY):
					try:
						os.makedirs(self.DIRECTORY)
					except:
						self.session.open(MessageBox, _("Can't create backup directory"), MessageBox.TYPE_ERROR, timeout=10)
						return
				self.SLOT = answer[1]
				self.MODEL = GetBoxName()
				self.OEM = getBrandOEM()
				self.MACHINEBUILD = getMachineBuild()
				self.MACHINENAME = getMachineName()
				self.MACHINEBRAND = getMachineBrand()
				self.IMAGEFOLDER = getImageFolder()
				self.UBINIZE_ARGS = getMachineUBINIZE()
				self.MKUBIFS_ARGS = getMachineMKUBIFS()
				self.ROOTFSSUBDIR = "none"
				self.ROOTFSBIN = getMachineRootFile()
				self.KERNELBIN = getMachineKernelFile()
				self.ROOTFSTYPE = getImageFileSystem().strip()
				self.IMAGEDISTRO = getImageDistro()
				self.DISTROVERSION = getImageVersion()

				if SystemInfo["canRecovery"]:
					self.EMMCIMG = SystemInfo["canRecovery"][0]
					self.MTDBOOT = SystemInfo["canRecovery"][1]
				else:
					self.EMMCIMG = "none"
					self.MTDBOOT = "none"

				self.getImageList = self.saveImageList
				if SystemInfo["canMultiBoot"]:
					self.MTDKERNEL = SystemInfo["canMultiBoot"][self.SLOT]["kernel"].split('/')[2]
					self.MTDROOTFS = SystemInfo["canMultiBoot"][self.SLOT]["device"].split('/')[2]
					if 'rootsubdir' in SystemInfo["canMultiBoot"][self.SLOT]:
						self.ROOTFSSUBDIR = SystemInfo["canMultiBoot"][self.SLOT]['rootsubdir']
				else:
					self.MTDKERNEL = getMachineMtdKernel()
					self.MTDROOTFS = getMachineMtdRoot()

				print "[Image Backup] BOX MACHINEBUILD = >%s<" % self.MACHINEBUILD
				print "[Image Backup] BOX MACHINENAME = >%s<" % self.MACHINENAME
				print "[Image Backup] BOX MACHINEBRAND = >%s<" % self.MACHINEBRAND
				print "[Image Backup] BOX MODEL = >%s<" % self.MODEL
				print "[Image Backup] OEM MODEL = >%s<" % self.OEM
				print "[Image Backup] IMAGEFOLDER = >%s<" % self.IMAGEFOLDER
				print "[Image Backup] UBINIZE = >%s<" % self.UBINIZE_ARGS
				print "[Image Backup] MKUBIFS = >%s<" % self.MKUBIFS_ARGS
				print "[Image Backup] MTDBOOT = >%s<" % self.MTDBOOT
				print "[Image Backup] MTDKERNEL = >%s<" % self.MTDKERNEL
				print "[Image Backup] MTDROOTFS = >%s<" % self.MTDROOTFS
				print "[Image Backup] ROOTFSBIN = >%s<" % self.ROOTFSBIN
				print "[Image Backup] KERNELBIN = >%s<" % self.KERNELBIN
				print "[Image Backup] ROOTFSSUBDIR = >%s<" % self.ROOTFSSUBDIR
				print "[Image Backup] ROOTFSTYPE = >%s<" % self.ROOTFSTYPE
				print "[Image Backup] EMMCIMG = >%s<" % self.EMMCIMG
				print "[Image Backup] IMAGEDISTRO = >%s<" % self.IMAGEDISTRO
				print "[Image Backup] DISTROVERSION = >%s<" % self.DISTROVERSION
				print "[Image Backup] MTDBOOT = >%s<" % self.MTDBOOT
				print "[Image Backup] USB RECOVERY = >%s< " % self.RECOVERY
				print "[Image Backup] DESTINATION = >%s< " % self.DIRECTORY
				print "[Image Backup] SLOT = >%s< " % self.SLOT

				self.TITLE = _("Full back-up on %s") % (self.DIRECTORY)
				self.START = time()
				self.DATE = strftime("%Y%m%d_%H%M", localtime(self.START))
				self.IMAGEVERSION = self.imageInfo()
				self.MKFS_UBI = "/usr/sbin/mkfs.ubifs"
				self.MKFS_TAR = "/bin/tar"
				self.BZIP2 = "/usr/bin/bzip2"
				self.MKFS_JFFS2 = "/usr/sbin/mkfs.jffs2"
				self.UBINIZE = "/usr/sbin/ubinize"
				self.NANDDUMP = "/usr/sbin/nanddump"
				self.FASTBOOT = "/usr/bin/ext2simg"
				self.WORKDIR = "%s/bi" % self.DIRECTORY

				self.SHOWNAME = "%s %s" % (self.MACHINEBRAND, self.MODEL)
				self.MAINDEST = "%s/build_%s/%s" % (self.DIRECTORY, self.MODEL, self.IMAGEFOLDER)
				self.MAINDESTROOT = "%s/build_%s" % (self.DIRECTORY, self.MODEL)

				self.message = "echo -e '\n"
				if getMachineBrand().startswith('A') or getMachineBrand().startswith('E') or getMachineBrand().startswith('I') or getMachineBrand().startswith('O') or getMachineBrand().startswith('U') or getMachineBrand().startswith('Xt'):
					self.message += (_('Back-up Tool for an %s\n') % self.SHOWNAME).upper()
				else:
					self.message += (_('Back-up Tool for a %s\n') % self.SHOWNAME).upper()
				self.message += VERSION + '\n'
				self.message += "_________________________________________________\n\n"
				self.message += _("Please be patient, a backup will now be made,\n")
				self.message += _("because of the used filesystem the back-up\n")
				if self.RECOVERY:
					self.message += _("will take about 30 minutes for this system\n")
				else:
					self.message += _("will take about 1-15 minutes for this system\n")
				self.message += "_________________________________________________\n"
				self.message += "'"

				## PREPARING THE BUILDING ENVIRONMENT
				os.system("rm -rf %s" % self.WORKDIR)
				self.backuproot = "/tmp/bi/root"
				if SystemInfo["canMultiBoot"]:
					if 'rootsubdir' in SystemInfo["canMultiBoot"][self.SLOT]:
						self.backuproot = "/tmp/bi/RootSubdir/"
				if not os.path.exists(self.WORKDIR):
					os.makedirs(self.WORKDIR)
				if not os.path.exists(self.backuproot):
					os.makedirs(self.backuproot)
				os.system("sync")
				if SystemInfo["canMultiBoot"]:
					if 'rootsubdir' in SystemInfo["canMultiBoot"][self.SLOT]:
						os.system("mount /dev/%s /tmp/bi/RootSubdir" % self.MTDROOTFS)
						self.backuproot = self.backuproot + self.ROOTFSSUBDIR
					else:
						os.system("mount /dev/%s %s" % (self.MTDROOTFS, self.backuproot))
				else:
					os.system("mount --bind / %s" % (self.backuproot))

				if "jffs2" in self.ROOTFSTYPE.split():
					cmd1 = "%s --root=%s --faketime --output=%s/root.jffs2 %s" % (self.MKFS_JFFS2, self.backuproot, self.WORKDIR, self.MKUBIFS_ARGS)
					cmd2 = None
					cmd3 = None
				elif "ubi" in self.ROOTFSTYPE.split():
					f = open("%s/ubinize.cfg" % self.WORKDIR, "w")
					f.write("[ubifs]\n")
					f.write("mode=ubi\n")
					f.write("image=%s/root.ubi\n" % self.WORKDIR)
					f.write("vol_id=0\n")
					f.write("vol_type=dynamic\n")
					f.write("vol_name=rootfs\n")
					f.write("vol_flags=autoresize\n")
					f.close()
					ff = open("%s/root.ubi" % self.WORKDIR, "w")
					ff.close()
					cmd1 = "%s -r %s -o %s/root.ubi %s" % (self.MKFS_UBI, self.backuproot, self.WORKDIR, self.MKUBIFS_ARGS)
					cmd2 = "%s -o %s/root.ubifs %s %s/ubinize.cfg" % (self.UBINIZE, self.WORKDIR, self.UBINIZE_ARGS, self.WORKDIR)
					cmd3 = "mv %s/root.ubifs %s/root.%s" % (self.WORKDIR, self.WORKDIR, self.ROOTFSTYPE)
				else:
					if self.EMMCIMG == "usb_update.bin" and self.RECOVERY:
						cmd1 = None
						cmd2 = None
					else:
						cmd1 = "%s -cf %s/rootfs.tar -C %s --exclude ./var/nmbd --exclude ./.resizerootfs --exclude ./.resize-rootfs --exclude ./.resize-linuxrootfs --exclude ./.resize-userdata --exclude ./var/lib/samba/private/msg.sock --exclude ./var/lib/samba/msg.sock/* --exclude ./run/avahi-daemon/socket ." % (self.MKFS_TAR, self.WORKDIR, self.backuproot)
						cmd2 = "%s %s/rootfs.tar" % (self.BZIP2, self.WORKDIR)
					cmd3 = None

				cmdlist = []
				cmdlist.append(self.message)
				if cmd1:
					cmdlist.append('echo "' + _("Create:") + ' %s"' % self.ROOTFSBIN)
					cmdlist.append(cmd1)
				if cmd2:
					cmdlist.append(cmd2)
				if cmd3:
					cmdlist.append(cmd3)

				if self.EMMCIMG == "usb_update.bin" and self.RECOVERY:
					SEEK_CONT = (Harddisk.getFolderSize(self.backuproot) / 1024) + 100000

					cmdlist.append('echo "' + _("Create:") + " fastboot dump" + '"')
					cmdlist.append('cp -f /usr/share/fastboot.bin %s/fastboot.bin' % (self.WORKDIR))
					#cmdlist.append("dd if=/dev/mmcblk0p1 of=%s/fastboot.bin" % self.WORKDIR)

					cmdlist.append('echo "' + _("Create:") + " bootargs dump" + '"')
					cmdlist.append('cp -f /usr/share/bootargs.bin %s/bootargs.bin' % (self.WORKDIR))
					#cmdlist.append("dd if=/dev/mmcblk0p2 of=%s/bootargs.bin" % self.WORKDIR)

					cmdlist.append('echo "' + _("Create:") + " boot dump" + '"')
					cmdlist.append("dd if=/dev/mmcblk0p3 of=%s/boot.img" % self.WORKDIR)

					cmdlist.append('echo "' + _("Create:") + " baseparam dump" + '"')
					#cmdlist.append('cp -f /usr/share/bootargs.bin %s/baseparam.img' %(self.WORKDIR))
					cmdlist.append("dd if=/dev/mmcblk0p4 of=%s/baseparam.img" % self.WORKDIR)

					cmdlist.append('echo "' + _("Create:") + " pq_param dump" + '"')
					#cmdlist.append('cp -f /usr/share/bootargs.bin %s/pq_param.bin' %(self.WORKDIR))
					cmdlist.append("dd if=/dev/mmcblk0p5 of=%s/pq_param.bin" % self.WORKDIR)

					cmdlist.append('echo "' + _("Create:") + " logo dump" + '"')
					cmdlist.append("dd if=/dev/mmcblk0p6 of=%s/logo.img" % self.WORKDIR)

					cmdlist.append('echo "' + _("Create:") + " deviceinfo dump" + '"')
					#cmdlist.append('cp -f /usr/share/bootargs.bin %s/deviceinfo.bin' %(self.WORKDIR))
					cmdlist.append("dd if=/dev/mmcblk0p7 of=%s/deviceinfo.bin" % self.WORKDIR)

					cmdlist.append('echo "' + _("Create:") + " apploader dump" + '"')
					cmdlist.append('cp -f /usr/share/apploader.bin %s/apploader.bin' % (self.WORKDIR))
					#cmdlist.append("dd if=/dev/mmcblk0p10 of=%s/apploader.bin" % self.WORKDIR)

					cmdlist.append('echo "' + _("Create:") + " rootfs dump" + '"')
					cmdlist.append("dd if=/dev/zero of=%s/rootfs.ext4 seek=%s count=60 bs=1024" % (self.WORKDIR, SEEK_CONT))
					cmdlist.append("mkfs.ext4 -F -i 4096 %s/rootfs.ext4" % (self.WORKDIR))
					cmdlist.append("mkdir -p %s/userdata" % self.WORKDIR)
					cmdlist.append("mount %s/rootfs.ext4 %s/userdata" % (self.WORKDIR, self.WORKDIR))
					cmdlist.append("mkdir -p %s/userdata/linuxrootfs1" % self.WORKDIR)
					cmdlist.append("mkdir -p %s/userdata/linuxrootfs2" % self.WORKDIR)
					cmdlist.append("mkdir -p %s/userdata/linuxrootfs3" % self.WORKDIR)
					cmdlist.append("mkdir -p %s/userdata/linuxrootfs4" % self.WORKDIR)
					cmdlist.append("rsync -aAX %s/ %s/userdata/linuxrootfs1/" % (self.backuproot, self.WORKDIR))
					cmdlist.append("umount %s/userdata" % (self.WORKDIR))

				cmdlist.append('echo "' + _("Create:") + " kerneldump" + '"')
				if SystemInfo["canMultiBoot"] or self.MTDKERNEL.startswith('mmcblk0'):
					cmdlist.append("dd if=/dev/%s of=%s/%s" % (self.MTDKERNEL, self.WORKDIR, self.KERNELBIN))
				else:
					cmdlist.append("nanddump -a -f %s/vmlinux.gz /dev/%s" % (self.WORKDIR, self.MTDKERNEL))

				if self.EMMCIMG == "usb_update.bin" and self.RECOVERY:
					cmdlist.append('echo "' + _("Create: Recovery Fullbackup %s") % (self.EMMCIMG) + '"')
					f = open("%s/emmc_partitions.xml" % self.WORKDIR, "w")
					f.write('<?xml version="1.0" encoding="GB2312" ?>\n')
					f.write('<Partition_Info>\n')
					f.write('<Part Sel="1" PartitionName="fastboot" FlashType="emmc" FileSystem="none" Start="0" Length="1M" SelectFile="fastboot.bin"/>\n')
					f.write('<Part Sel="1" PartitionName="bootargs" FlashType="emmc" FileSystem="none" Start="1M" Length="1M" SelectFile="bootargs.bin"/>\n')
					f.write('<Part Sel="1" PartitionName="bootoptions" FlashType="emmc" FileSystem="none" Start="2M" Length="1M" SelectFile="boot.img"/>\n')
					f.write('<Part Sel="1" PartitionName="baseparam" FlashType="emmc" FileSystem="none" Start="3M" Length="3M" SelectFile="baseparam.img"/>\n')
					f.write('<Part Sel="1" PartitionName="pqparam" FlashType="emmc" FileSystem="none" Start="6M" Length="4M" SelectFile="pq_param.bin"/>\n')
					f.write('<Part Sel="1" PartitionName="logo" FlashType="emmc" FileSystem="none" Start="10M" Length="4M" SelectFile="logo.img"/>\n')
					f.write('<Part Sel="1" PartitionName="deviceinfo" FlashType="emmc" FileSystem="none" Start="14M" Length="4M" SelectFile="deviceinfo.bin"/>\n')
					f.write('<Part Sel="1" PartitionName="loader" FlashType="emmc" FileSystem="none" Start="26M" Length="32M" SelectFile="apploader.bin"/>\n')
					f.write('<Part Sel="1" PartitionName="linuxkernel1" FlashType="emmc" FileSystem="none" Start="66M" Length="16M" SelectFile="kernel.bin"/>\n')
					if self.MACHINENAME in ("sf8008m"):
						f.write('<Part Sel="1" PartitionName="userdata" FlashType="emmc" FileSystem="ext3/4" Start="130M" Length="3580M" SelectFile="rootfs.ext4"/>\n')
					else:
						f.write('<Part Sel="1" PartitionName="userdata" FlashType="emmc" FileSystem="ext3/4" Start="130M" Length="7000M" SelectFile="rootfs.ext4"/>\n')
					f.write('</Partition_Info>\n')
					f.close()
					cmdlist.append('mkupdate -s 00000003-00000001-01010101 -f %s/emmc_partitions.xml -d %s/%s' % (self.WORKDIR, self.WORKDIR, self.EMMCIMG))

				self.session.open(Console, title=self.TITLE, cmdlist=cmdlist, finishedCallback=self.doFullBackupCB, closeOnSuccess=True)

			else:
				self.close()
		else:
			self.close()

	def doFullBackupCB(self):
		cmdlist = []
		cmdlist.append(self.message)
		cmdlist.append('echo "' + _("Almost there... ") + '"')
		cmdlist.append('echo "' + _("Now building the Backup Image") + '"')

		if self.EMMCIMG == "usb_update.bin" and self.RECOVERY:
			os.system('rm -rf %s' % self.MAINDESTROOT)
			if not os.path.exists(self.MAINDESTROOT):
				os.makedirs(self.MAINDESTROOT)
			f = open("%s/imageversion" % self.MAINDESTROOT, "w")
			f.write(self.IMAGEVERSION)
			f.close()
		else:
			os.system('rm -rf %s' % self.MAINDEST)
			if not os.path.exists(self.MAINDEST):
				os.makedirs(self.MAINDEST)
			f = open("%s/imageversion" % self.MAINDEST, "w")
			f.write(self.IMAGEVERSION)
			f.close()

			if self.ROOTFSBIN == "rootfs.tar.bz2":
				os.system('mv %s/rootfs.tar.bz2 %s/rootfs.tar.bz2' % (self.WORKDIR, self.MAINDEST))
			else:
				os.system('mv %s/root.%s %s/%s' % (self.WORKDIR, self.ROOTFSTYPE, self.MAINDEST, self.ROOTFSBIN))
			if SystemInfo["canMultiBoot"] or self.MTDKERNEL.startswith('mmcblk0'):
				os.system('mv %s/%s %s/%s' % (self.WORKDIR, self.KERNELBIN, self.MAINDEST, self.KERNELBIN))
			else:
				os.system('mv %s/vmlinux.gz %s/%s' % (self.WORKDIR, self.MAINDEST, self.KERNELBIN))

		if self.RECOVERY:
			if self.EMMCIMG == "usb_update.bin":
				os.system('mv %s/%s %s/%s' % (self.WORKDIR, self.EMMCIMG, self.MAINDESTROOT, self.EMMCIMG))
				cmdlist.append('cp -f /usr/share/fastboot.bin %s/fastboot.bin' % (self.MAINDESTROOT))
				cmdlist.append('cp -f /usr/share/bootargs.bin %s/bootargs.bin' % (self.MAINDESTROOT))
				cmdlist.append('cp -f /usr/share/apploader.bin %s/apploader.bin' % (self.MAINDESTROOT))
			else:
				os.system('mv %s/%s %s/%s' % (self.WORKDIR, self.EMMCIMG, self.MAINDEST, self.EMMCIMG))
		elif self.MODEL in ('viperslim', 'evoslimse', 'evoslimt2c', "novaip", "zgemmai55", "sf98", "xpeedlxpro", 'evoslim', 'vipert2c'):
			cmdlist.append('echo "This file forces the update." > %s/force' % self.MAINDEST)
		elif SystemInfo["canMultiBoot"] and 'rootsubdir' in SystemInfo["canMultiBoot"][self.SLOT]:
			cmdlist.append('echo "Rename the unforce_%s.txt to force_%s.txt and move it to the root of your usb-stick" > %s/force_%s_READ.ME' % (self.MACHINEBUILD, self.MACHINEBUILD, self.MAINDEST, self.MACHINEBUILD))
			cmdlist.append('echo "When you enter the recovery menu then it will force to install the image in the linux1 selection" >> %s/force_%s_READ.ME' % (self.MAINDEST, self.MACHINEBUILD))
		else:
			cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/noforce' % self.MAINDEST)

		if self.MODEL in ("gbquad", "gbquadplus", "gb800ue", "gb800ueplus", "gbultraue", "gbultraueh", "twinboxlcd", "twinboxlcdci", "singleboxlcd", "sf208", "sf228"):
			lcdwaitkey = '/usr/share/lcdwaitkey.bin'
			lcdwarning = '/usr/share/lcdwarning.bin'
			if os.path.isfile(lcdwaitkey):
				os.system('cp %s %s/lcdwaitkey.bin' % (lcdwaitkey, self.MAINDEST))
			if os.path.isfile(lcdwarning):
				os.system('cp %s %s/lcdwarning.bin' % (lcdwarning, self.MAINDEST))

		if SystemInfo["canRecovery"] and self.RECOVERY:
			cmdlist.append('7za a -r -bt -bd %s/%s-%s-%s-backup-%s_recovery_emmc.zip %s/*' % (self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE, self.MAINDESTROOT))
		elif SystemInfo["canMultiBoot"] and 'rootsubdir' in SystemInfo["canMultiBoot"][self.SLOT]:
			cmdlist.append('echo "rename this file to "force" to force an update without confirmation" > %s/unforce_%s.txt' % (self.MAINDESTROOT, self.MACHINEBUILD))
			cmdlist.append('7za a -r -bt -bd %s/%s-%s-%s-backup-%s_mmc.zip %s/*' % (self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE, self.MAINDESTROOT))
		else:
			cmdlist.append('7za a -r -bt -bd %s/%s-%s-%s-backup-%s_usb.zip %s/*' % (self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE, self.MAINDESTROOT))

		cmdlist.append("sync")
		file_found = True

		if self.EMMCIMG == "usb_update.bin" and self.RECOVERY:
			if not os.path.isfile("%s/%s" % (self.MAINDESTROOT, self.EMMCIMG)):
				print "[Image Backup] %s file not found" % (self.EMMCIMG)
				file_found = False
		else:
			if not os.path.isfile("%s/%s" % (self.MAINDEST, self.ROOTFSBIN)):
				print "[Image Backup] %s file not found" % (self.ROOTFSBIN)
				file_found = False

			if not os.path.isfile("%s/%s" % (self.MAINDEST, self.KERNELBIN)):
				print "[Image Backup] %s file not found" % (self.KERNELBIN)
				file_found = False

		if SystemInfo["canMultiBoot"] and not self.RECOVERY and not 'rootsubdir' in SystemInfo["canMultiBoot"][self.SLOT]:
			cmdlist.append('echo "_________________________________________________\n"')
			cmdlist.append('echo "' + _("Multiboot Image created on: %s/%s-%s-%s-backup-%s_usb.zip") % (self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE) + '"')
			cmdlist.append('echo "_________________________________________________"')
			cmdlist.append('echo " "')
			cmdlist.append('echo "' + _("Please wait...almost ready! ") + '"')
			cmdlist.append('echo " "')
			cmdlist.append('echo "' + _("To restore the image:") + '"')
			cmdlist.append('echo "' + _("Use OnlineFlash in SoftwareManager") + '"')
		elif file_found:
			cmdlist.append('echo "_________________________________________________\n"')

			if SystemInfo["canRecovery"] and self.RECOVERY:
				cmdlist.append('echo "' + _("Image created on: %s/%s-%s-%s-backup-%s_recovery_emmc.zip") % (self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE) + '"')
			elif SystemInfo["canMultiBoot"] and 'rootsubdir' in SystemInfo["canMultiBoot"][self.SLOT]:
				cmdlist.append('echo "' + _("Image created on: %s/%s-%s-%s-backup-%s_mmc.zip") % (self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE) + '"')
			else:
				cmdlist.append('echo "' + _("Image created on: %s/%s-%s-%s-backup-%s_usb.zip") % (self.DIRECTORY, self.IMAGEDISTRO, self.DISTROVERSION, self.MODEL, self.DATE) + '"')
			cmdlist.append('echo "_________________________________________________"')
			cmdlist.append('echo " "')
			cmdlist.append('echo "' + _("Please wait...almost ready! ") + '"')
			cmdlist.append('echo " "')
			cmdlist.append('echo "' + _("To restore the image:") + '"')
			cmdlist.append('echo "' + _("Please check the manual of the receiver") + '"')
			cmdlist.append('echo "' + _("on how to restore the image") + '"')
		else:
			cmdlist.append('echo "_________________________________________________\n"')
			cmdlist.append('echo "' + _("Image creation failed - ") + '"')
			cmdlist.append('echo "' + _("Probable causes could be") + ':"')
			cmdlist.append('echo "' + _("     wrong back-up destination ") + '"')
			cmdlist.append('echo "' + _("     no space left on back-up device") + '"')
			cmdlist.append('echo "' + _("     no writing permission on back-up device") + '"')
			cmdlist.append('echo " "')

		cmdlist.append("rm -rf %s/build_%s" % (self.DIRECTORY, self.MODEL))
		if SystemInfo["canMultiBoot"] and 'rootsubdir' in SystemInfo["canMultiBoot"][self.SLOT]:
			cmdlist.append("umount /tmp/bi/RootSubdir")
			cmdlist.append("rmdir /tmp/bi/RootSubdir")
		else:
			cmdlist.append("umount /tmp/bi/root")
			cmdlist.append("rmdir /tmp/bi/root")
		cmdlist.append("rmdir /tmp/bi")
		cmdlist.append("rm -rf %s" % self.WORKDIR)
		cmdlist.append("sleep 5")
		END = time()
		DIFF = int(END - self.START)
		TIMELAP = str(datetime.timedelta(seconds=DIFF))
		cmdlist.append('echo "' + _("Time required for this process: %s") % TIMELAP + '\n"')

		self.session.open(Console, title=self.TITLE, cmdlist=cmdlist, closeOnSuccess=False)

	def imageInfo(self):
		AboutText = _("Full Image Backup ")
		AboutText += _("By OpenEight Image Team") + "\n"
		AboutText += _("Support at") + " www.octagon-forum.eu\n\n"
		AboutText += _("[Image Info]\n")
		AboutText += _("Model: %s %s\n") % (getMachineBrand(), getMachineName())
		AboutText += _("Backup Date: %s\n") % strftime("%Y-%m-%d", localtime(self.START))

		if os.path.exists('/proc/stb/info/chipset'):
			AboutText += _("Chipset: BCM%s") % about.getChipSetString().lower().replace('\n', '').replace('bcm', '') + "\n"

		AboutText += _("CPU: %s") % about.getCPUInfoString() + "\n"
		AboutText += _("Cores: %s") % about.getCpuCoresString() + "\n"

		AboutText += _("Version: %s") % getImageVersion() + "\n"
		AboutText += _("Build: %s") % getImageBuild() + "\n"
		AboutText += _("Kernel: %s") % about.getKernelVersionString() + "\n"

		string = getDriverDate()
		year = string[0:4]
		month = string[4:6]
		day = string[6:8]
		driversdate = '-'.join((year, month, day))
		AboutText += _("Drivers:\t%s") % driversdate + "\n"

		AboutText += _("Last update:\t%s") % getEnigmaVersionString() + "\n\n"

		AboutText += _("[Enigma2 Settings]\n")
		AboutText += commands.getoutput("cat /etc/enigma2/settings")
		AboutText += _("\n\n[User - bouquets (TV)]\n")
		try:
			f = open("/etc/enigma2/bouquets.tv", "r")
			lines = f.readlines()
			f.close()
			for line in lines:
				if line.startswith("#SERVICE:"):
					bouqet = line.split()
					if len(bouqet) > 3:
						bouqet[3] = bouqet[3].replace('"', '')
						f = open("/etc/enigma2/" + bouqet[3], "r")
						userbouqet = f.readline()
						AboutText += userbouqet.replace('#NAME ', '')
						f.close()
		except:
			AboutText += _("Error reading bouquets.tv")

		AboutText += _("\n[User - bouquets (RADIO)]\n")
		try:
			f = open("/etc/enigma2/bouquets.radio", "r")
			lines = f.readlines()
			f.close()
			for line in lines:
				if line.startswith("#SERVICE:"):
					bouqet = line.split()
					if len(bouqet) > 3:
						bouqet[3] = bouqet[3].replace('"', '')
						f = open("/etc/enigma2/" + bouqet[3], "r")
						userbouqet = f.readline()
						AboutText += userbouqet.replace('#NAME ', '')
						f.close()
		except:
			AboutText += _("Error reading bouquets.radio")

		AboutText += _("\n[Installed Plugins]\n")
		AboutText += commands.getoutput("opkg list_installed | grep enigma2-plugin-")

		return AboutText
