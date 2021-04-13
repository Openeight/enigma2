# for localized messages
from . import _
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.Label import Label
from Components.Language import language
from Components.Button import Button
from Components.MenuList import MenuList
from Components.Sources.List import List
from Screens.Standby import TryQuitMainloop
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_SKIN
from os import listdir, remove, mkdir, path, access, X_OK, chmod, system
import datetime
import time


class ScriptRunner(Screen):
	skin = """<screen name="ScriptRunner" position="center,center" size="560,400" title="Script Runner" flags="wfBorder" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
		<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
		<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
		<widget name="key_yellow" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
		<widget name="key_blue" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		<widget name="lab1" position="0,50" size="560,50" font="Regular; 20" zPosition="2" transparent="0" halign="center"/>
		<widget name="list" position="10,105" size="540,300" scrollbarMode="showOnDemand" />
		<applet type="onLayoutFinish">
			self["list"].instance.setItemHeight(25)
		</applet>
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Job Manager"))
		self['lab1'] = Label()
		self.list = []
		self.execute = ""
		self.populate_List()
		self['list'] = MenuList(self.list)
		self['myactions'] = ActionMap(['ColorActions', 'OkCancelActions', 'DirectionActions'],
			{
				'cancel': self.close,
				'red': self.close,
				'green': self.green,
				'yellow': self.yellow,
				'blue': self.blue,
				'ok': self.green,
			}, -1)

		self["key_red"] = Button(_("Close"))
		self["key_green"] = Button(_("Run"))
		self["key_yellow"] = Button(_("Run in the background"))
		self["key_blue"] = Button(_("Run and Close on success"))

	def populate_List(self):
		if not path.exists('/usr/script'):
			mkdir('/usr/script', 0755)
		self['lab1'].setText(_("Select a script to run:"))
		del self.list[:]
		f = listdir('/usr/script')
		for line in f:
			parts = line.split()
			pkg = parts[0]
			if pkg.find('.sh') >= 0:
				self.list.append(pkg)
		self.list.sort()

	def green(self):
		self.execute = "0"
		self.runscript()

	def yellow(self):
		self.execute = "1"
		self.runscript()

	def blue(self):
		self.execute = "2"
		self.runscript()

	def runscript(self):
		self.sel = self['list'].getCurrent()
		if self.sel:
			message = _("Are you ready to run the script ?")
			ybox = self.session.openWithCallback(self.Run, MessageBox, message, MessageBox.TYPE_YESNO)
			ybox.setTitle(_("Run Confirmation"))
		else:
			self.session.open(MessageBox, _("You have no script to run."), MessageBox.TYPE_INFO, timeout=10)

	def Run(self, answer):
		if answer is True:
			system("if awk '/\r$/{exit 0;} 1{exit 1;}' /usr/script/" + self.sel + " ; then dos2unix /usr/script/" + self.sel + "; fi")
			if not access("/usr/script/" + self.sel, X_OK):
				chmod("/usr/script/" + self.sel, 0755)
			cmd1 = ". /usr/script/" + self.sel
			if ".hidden." in self.sel:
				self.execute = "1"
			elif ".close." in self.sel:
				self.execute = "2"
			if self.execute == "1":
				from enigma import eConsoleAppContainer
				eConsoleAppContainer().execute(cmd1)
			elif self.execute == "2":
				self.session.open(Console, title=self.sel, cmdlist=[cmd1], closeOnSuccess=True)
			else:
				self.session.open(Console, title=self.sel, cmdlist=[cmd1])

	def myclose(self):
		self.close()
