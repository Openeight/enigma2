from Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.Harddisk import harddiskmanager
from Components.NimManager import nimmanager
from Components.About import about
from Components.ScrollLabel import ScrollLabel
from Components.Button import Button
from Tools.Downloader import downloadWithProgress
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubsection, ConfigSelection, getConfigListEntry
from Components.Label import Label
import re
from boxbranding import getBoxType, getMachineBrand, getMachineName, getImageVersion, getImageBuild, getDriverDate
from os import path
from Tools.StbHardware import getFPVersion
from enigma import eTimer

config.CommitInfoSetup = ConfigSubsection()
config.CommitInfoSetup.commiturl = ConfigSelection(default='Enigma2', choices=[('Enigma2', _('Source-Enigma2')), ('XTA', _('Skin-XTA')), ('TechniHD', _('Skin-TechniHD'))])

class About(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)


		AboutText = _("Model: %s %s") % (getMachineBrand(), getMachineName()) + "\n"
		AboutText += _("Image: ") + about.getImageTypeString() + "\n"
		AboutText += _("Kernel version: ") + about.getKernelVersionString() + "\n"                             
                if path.exists('/proc/stb/info/chipset'):
			AboutText += _("Chipset: %s") % about.getChipSetString() + "\n"
                AboutText += _("CPU: %s") % about.getCPUString() + "\n"
		AboutText += _("Cores: %s") % about.getCpuCoresString() + "\n"
                AboutText += _("Version: %s") % getImageVersion() + "\n"
		AboutText += _("Build: %s") % getImageBuild() + "\n"
                string = getDriverDate()
		year = string[0:4]
		month = string[4:6]
		day = string[6:8]
		driversdate = '-'.join((year, month, day))
		AboutText += _("Drivers: %s") % driversdate + "\n"
                EnigmaVersion = "Enigma: " + about.getEnigmaVersionString()
		self["EnigmaVersion"] = StaticText(EnigmaVersion)
		AboutText += EnigmaVersion + "\n"

		ImageVersion = _("Last upgrade: ") + about.getImageVersionString()
		self["ImageVersion"] = StaticText(ImageVersion)
		AboutText += ImageVersion + "\n"

		fp_version = getFPVersion()
		if fp_version is None:
			fp_version = ""
		else:
			fp_version = _("Frontprocessor version: %d") % fp_version
			AboutText += fp_version + "\n"

		self["FPVersion"] = StaticText(fp_version)

		self["TunerHeader"] = StaticText(_("Detected NIMs:"))
		AboutText += "\n" + _("Detected NIMs:") + "\n"

		nims = nimmanager.nimList()
		for count in range(len(nims)):
			if count < 4:
				self["Tuner" + str(count)] = StaticText(nims[count])
			else:
				self["Tuner" + str(count)] = StaticText("")
			AboutText += nims[count] + "\n"

		self["HDDHeader"] = StaticText(_("Detected HDD:"))
		AboutText += "\n" + _("Detected HDD:") + "\n"

		hddlist = harddiskmanager.HDDList()
		hddinfo = ""
		if hddlist:
			for count in range(len(hddlist)):
				if hddinfo:
					hddinfo += "\n"
				hdd = hddlist[count][1]
				if int(hdd.free()) > 1024:
					hddinfo += "%s\n(%s, %d GB %s)" % (hdd.model(), hdd.capacity(), hdd.free()/1024, _("free"))
				else:
					hddinfo += "%s\n(%s, %d MB %s)" % (hdd.model(), hdd.capacity(), hdd.free(), _("free"))
		else:
			hddinfo = _("none")
		self["hddA"] = StaticText(hddinfo)
		AboutText += hddinfo
		self["AboutScrollLabel"] = ScrollLabel(AboutText)
		self["key_green"] = Button(_("Translations"))
		self["key_red"] = Button(_("Latest Commits"))

		self["actions"] = ActionMap(["ColorActions", "SetupActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"red": self.showCommits,
				"green": self.showTranslationInfo,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			}, -2)

	def showTranslationInfo(self):
		self.session.open(TranslationInfo)

	def showCommits(self):
		self.session.open(CommitInfo)

class TranslationInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		# don't remove the string out of the _(), or it can't be "translated" anymore.

		# TRANSLATORS: Add here whatever should be shown in the "translator" about screen, up to 6 lines (use \n for newline)
		info = _("TRANSLATOR_INFO")

		if info == "TRANSLATOR_INFO":
			info = "(N/A)"

		infolines = _("").split("\n")
		infomap = {}
		for x in infolines:
			l = x.split(': ')
			if len(l) != 2:
				continue
			(type, value) = l
			infomap[type] = value
		print infomap

		self["TranslationInfo"] = StaticText(info)

		translator_name = infomap.get("Language-Team", "none")
		if translator_name == "none":
			translator_name = infomap.get("Last-Translator", "")

		self["TranslatorName"] = StaticText(translator_name)

		self["actions"] = ActionMap(["SetupActions"],
			{
				"cancel": self.close,
				"ok": self.close,
			}, -2)

class CommitInfo(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = ["CommitInfo", "About"]
		self["AboutScrollLabel"] = ScrollLabel(_("Please wait"))
                self["Commits"] = Label()
		self["actions"] = ActionMap(["ColorActions", "OkCancelActions", "SetupActions", "DirectionActions"],
			{
				"cancel": self.close,
				"ok": self.close,
				"menu": self.keyMenu,
				"up": self["AboutScrollLabel"].pageUp,
				"down": self["AboutScrollLabel"].pageDown
			}, -2)

		self.Timer = eTimer()
		self.Timer.callback.append(self.downloadWebSite)
		self.Timer.start(50, True)

	def downloadWebSite(self):
                if config.CommitInfoSetup.commiturl.value == 'Enigma2':
                        self["Commits"].setText("Enigma2")
                        url = 'http://github.com/XTAv2/Enigma2/commits/master'
		elif config.CommitInfoSetup.commiturl.value == 'XTA':
		        self["Commits"].setText("XTA")
                        url = 'http://github.com/XTAv2/xta/commits/master'
                elif config.CommitInfoSetup.commiturl.value == 'TechniHD':
                        self["Commits"].setText("TechniHD")
                        url = 'http://github.com/XTAv2/TechniHD/commits/master'
		download = downloadWithProgress(url, '/tmp/.commits')
		download.start().addCallback(self.download_finished).addErrback(self.download_failed)

	def download_failed(self, failure_instance=None, error_message=""):
		self["AboutScrollLabel"].setText(_("Currently the commit log cannot be retreived - please try later again"))

	def download_finished(self, string=""):
		commitlog = ""
		try:
			for x in  "".join(open('/tmp/.commits', 'r').read().split('<li class="commit commit-group-item js-navigation-item js-details-container">')[1:]).split('<p class="commit-title  js-pjax-commit-title">'):
				title = re.findall('class="message" data-pjax="true" title="(.*?)"', x, re.DOTALL)
				author = re.findall('rel="author">(.*?)</', x)
				date   = re.findall('<time class="js-relative-date" datetime=".*?" title="(.*?)">', x)
				for t in title:
					commitlog += t.strip().replace('&amp;', '&').replace('&quot;', '"').replace('&lt;', '\xc2\xab').replace('&gt;', '\xc2\xbb') + "\n"
				for a in author:
					commitlog += "Author: " + a.strip().replace('&lt;', '\xc2\xab').replace('&gt;', '\xc2\xbb') + "\n"
				for d in date:
					commitlog += d.strip() + "\n"
				commitlog += 140*'-' + "\n"
		except:
			commitlog = _("Currently the commit log cannot be retrieved - please try later again")
		self["AboutScrollLabel"].setText(commitlog)
	
	def keyMenu(self):
                self.session.open(CommitInfoSetup)

        def showTranslationInfo(self):
		self.session.open(TranslationInfo)

	def showAbout(self):
		self.session.open(About)

class CommitInfoSetup(Screen, ConfigListScreen):
        skin = """
	    <screen position="c-300,c-250" size="600,200" title="openXTA CommitInfoSetup">
		    <widget name="config" position="25,25" scrollbarMode="showOnDemand" size="550,400" />
		    <ePixmap pixmap="skin_default/buttons/red.png" position="20,e-45" size="140,40" alphatest="on" />
		    <ePixmap pixmap="skin_default/buttons/green.png" position="160,e-45" size="140,40" alphatest="on" />
		    <widget source="key_red" render="Label" position="20,e-45" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		    <widget source="key_green" render="Label" position="160,e-45" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
	    </screen>"""
	    
        def __init__(self, session):
                self.skin = CommitInfoSetup.skin
                Screen.__init__(self, session)
                self['key_red'] = StaticText(_('Cancel'))
                self['key_green'] = StaticText(_('OK'))
                self['actions'] = ActionMap(['SetupActions', 'ColorActions', 'EPGSelectActions', 'NumberActions'], 
                {'ok': self.keyGo,
                 'left': self.keyLeft,
                 'right': self.keyRight,
                 'save': self.keyGo,
                 'cancel': self.keyCancel,
                 'green': self.keyGo,
                 'red': self.keyCancel}, -2)
                  
                self.list = []
                ConfigListScreen.__init__(self, self.list, session=self.session)
                self.list.append(getConfigListEntry(_('Select CommitInfo Log'), config.CommitInfoSetup.commiturl))
                self['config'].list = self.list
                self['config'].l.setList(self.list)
        
        def keyLeft(self):
                ConfigListScreen.keyLeft(self)

        def keyRight(self):
                ConfigListScreen.keyRight(self)
        
        def keyGo(self):
                for x in self['config'].list:
                        x[1].save()
                        
                self.close()
                 
        def keyCancel(self):
                for x in self['config'].list:
                        x[1].cancel()

                self.close()
