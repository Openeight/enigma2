from Components.About import about
from Components.Console import Console
from Components.config import config, configfile
from Components.Pixmap import Pixmap, MovingPixmap, MultiPixmap
from Components.Harddisk import harddiskmanager
from Screens.Wizard import wizardManager, WizardSummary
from Screens.WizardLanguage import WizardLanguage
from Screens.Rc import Rc
from Screens.MessageBox import MessageBox
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_PLUGINS
from BackupRestore import RestoreMenu
from os import mkdir, listdir, path, walk
from boxbranding import getBoxType

boxtype = getBoxType()

def listConfigBackup():
	try:
		devices = [(r.description, r.mountpoint) for r in harddiskmanager.getMountedPartitions(onlyhotplug = False)]
		list = []
		files = []
		for x in devices:
			if x[1] == '/':
				devices.remove(x)
		if len(devices):
			for x in devices:
				devpath = path.join(x[1], 'backup_' + boxtype)
				if path.exists(devpath):
					try:
						files = listdir(devpath)
					except:
						files = []
				else:
					devpath = path.join(x[1], 'backup')
					if path.exists(devpath):
						try:
							files = listdir(devpath)
						except:
							files = []
					else:
						files = []
				if len(files):
					for file in files:
						if file.endswith('.tar.gz'):
							list.append((path.join(devpath,file),path.join(devpath,file)))
		if len(list):
			list.sort()
			list.reverse()
			return list
		else:
			return None
	except IOError, e:
		print "unable to use device (%s)..." % str(e)
		return None

if listConfigBackup() is None:
	backupAvailable = 0
else:
	backupAvailable = 1

class RestoreWizard(WizardLanguage, Rc):
	def __init__(self, session):
		self.xmlfile = resolveFilename(SCOPE_PLUGINS, "SystemPlugins/SoftwareManager/restorewizard.xml")
		WizardLanguage.__init__(self, session, showSteps = False, showStepSlider = False)
		Rc.__init__(self)
		self.session = session
		self.skinName = "StartWizard"
		self.skin = "StartWizard.skin"
		self["wizard"] = Pixmap()
		self.selectedAction = None
		self.NextStep = None
		self.Text = None
		self.buildListRef = None
		self.fullbackupfilename = None

	def markDone(self):
		pass

	def listRestore(self):
		list = []
		list.append((_("Ok, to perform a restore"), "settingsrestore"))
		list.append((_("Exit the restore wizard"), "end"))
		return list

	def ActionSelectionMade(self, index):
		self.selectedAction = index
		self.ActionSelect(index)

	def ActionSelect(self, index):
		self.NextStep = index

	def ActionSelectionMoved(self):
		self.ActionSelect(self.selection)

	def buildList(self, action):
		# print 'self.NextStep ',self.NextStep
		if self.NextStep is 'end':
			self.buildListfinishedCB(False)
		if self.NextStep is 'settingsrestore':
			self.session.open(RestoreMenu, self.skin)

	def buildListfinishedCB(self,data):
		self.buildListRef = None
		if data is True:
			self.currStep = self.getStepWithID(self.NextStep)
			self.afterAsyncCode()
		else:
			self.currStep = self.getStepWithID(self.NextStep)
			self.afterAsyncCode()

