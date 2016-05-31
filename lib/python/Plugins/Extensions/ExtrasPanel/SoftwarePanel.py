from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.About import * 
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Ipkg import IpkgComponent
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.LoadPixmap import LoadPixmap
from enigma import ePixmap
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN, SCOPE_CURRENT_SKIN, SCOPE_METADIR
import os

class SoftwarePanel(Screen):

	def __init__(self, session, *args):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Openeight Software Panel"))
		skin = """
		<screen name="SoftwarePanel" position="center,center" size="650,605" title="Software Panel">
			<widget name="a_off" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/pics/aoff.png" position="10,10" zPosition="1" size="36,97" alphatest="on" />
			<widget name="a_red" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/pics/ared.png" position="10,10" zPosition="1" size="36,97" alphatest="on" />
			<widget name="a_yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/pics/ayellow.png" position="10,10" zPosition="1" size="36,97" alphatest="on" />
			<widget name="a_green" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/pics/agreen.png" position="10,10" zPosition="1" size="36,97" alphatest="on" />
			<widget name="feedstatusRED" position="60,14" size="200,30" zPosition="1" font="Regular;25" halign="left" transparent="1" />
			<widget name="feedstatusYELLOW" position="60,46" size="200,30" zPosition="1" font="Regular;25" halign="left" transparent="1" />
			<widget name="feedstatusGREEN" position="60,78" size="200,30" zPosition="1" font="Regular;25" halign="left" transparent="1" />
			<widget name="packagetext" position="276,50" size="247,30" zPosition="1" font="Regular;25" halign="right" transparent="1" />
			<widget name="packagenr" position="529,50" size="69,30" zPosition="1" font="Regular;25" halign="left" transparent="1" />
			<widget source="list" render="Listbox" position="10,120" size="630,365" scrollbarMode="showOnDemand">
				<convert type="TemplatedMultiContent">
					{"template": [
							MultiContentEntryText(pos = (5, 1), size = (540, 28), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 0 is the name
							MultiContentEntryText(pos = (5, 26), size = (540, 20), font=1, flags = RT_HALIGN_LEFT, text = 2), # index 2 is the description
							MultiContentEntryPixmapAlphaTest(pos = (545, 2), size = (48, 48), png = 4), # index 4 is the status pixmap
							MultiContentEntryPixmapAlphaTest(pos = (5, 50), size = (610, 2), png = 5), # index 4 is the div pixmap
						],
					"fonts": [gFont("Regular", 22),gFont("Regular", 14)],
					"itemHeight": 52
					}
				</convert>
			</widget>
			<ePixmap pixmap="skin_default/buttons/red.png" position="30,560" size="138,40" alphatest="blend" />
                        <widget name="key_green_pic" pixmap="skin_default/buttons/green.png" position="180,560" size="138,40" alphatest="blend" />
                        <ePixmap pixmap="skin_default/buttons/yellow.png" position="333,560" size="138,40" alphatest="blend" />
                        <ePixmap pixmap="skin_default/buttons/blue.png" position="481,560" size="138,40" alphatest="blend" />
                        <widget name="key_red" position="38,570" size="124,26" zPosition="1" font="Regular;17" halign="center" transparent="1" />
                        <widget name="key_green" position="188,570" size="124,26" zPosition="1" font="Regular;17" halign="center" transparent="1" />
                        <widget name="key_yellow" position="340,570" size="124,26" zPosition="1" font="Regular;17" halign="center" transparent="1" />
                        <widget name="key_blue" position="491,570" size="124,26" zPosition="1" font="Regular;17" halign="center" transparent="1" />
		</screen> """
		self.skin = skin
		self.list = []
		self.statuslist = []
		self["list"] = List(self.list)
		self['a_off'] = Pixmap()
		self['a_red'] = Pixmap()
		self['a_yellow'] = Pixmap()
		self['a_green'] = Pixmap()
		self['key_green_pic'] = Pixmap()
		self['key_red_pic'] = Pixmap()
		self['key_red'] = Label(_("Cancel"))
		self['key_green'] = Label(_("Update"))
		self['key_yellow'] = Label(_(""))
		self['packagetext'] = Label(_("Updates Available:"))
		self['packagenr'] = Label("0")
		self['feedstatusRED'] = Label("<  " + _("feed status"))
		self['feedstatusYELLOW'] = Label("<  " + _("feed status"))
		self['feedstatusGREEN'] = Label("<  " + _("feed status"))
		self['key_green'].hide()
		self['key_green_pic'].hide()
		self.update = False
		self.packages = 0
		self.trafficLight = 0
		self.ipkg = IpkgComponent()
		self.ipkg.addCallback(self.ipkgCallback)
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions", "SetupActions"],      
		{
			"cancel": self.Exit,
			"green": self.Green,
			"yellow": self.showCommitLog
		}, -2)

		self.onLayoutFinish.append(self.layoutFinished)

	def Exit(self):
		self.ipkg.stop()
		self.close()

	def Green(self):
		if self.packages > 0 and self.trafficLight > 0:
			if self.trafficLight == 1: # yellow
				message = _("The current image might not be stable.\nFor more information see %s.") % ("http://octagon-forum.eu")
				picon = MessageBox.TYPE_WARNING
			elif self.trafficLight == 2: # red
				message = _("The current image is not stable.\nFor more information see %s.") % ("http://octagon-forum.eu")
				picon = MessageBox.TYPE_ERROR
				self.session.open(MessageBox, message, type=MessageBox.TYPE_ERROR, picon=picon, timeout = 15, close_on_any_key=True)
				return
			elif self.trafficLight == 3: # unknown
				message = _("The status of the current image could not be checked because %s can not be reached.") % ("http://octagon-forum.eu")
				picon = MessageBox.TYPE_ERROR
			message += "\n" + _("Do you want to update your receiver?")
			self.session.openWithCallback(self.startActualUpdate, MessageBox, message, default = False, picon = picon)
		elif self.packages > 0:
				self.startActualUpdate(True)

	def showCommitLog(self):
		self.session.open(CommitInfo)

	def startActualUpdate(self, answer):
		if answer:
			from Plugins.SystemPlugins.SoftwareManager.plugin import UpdatePlugin
			self.session.open(UpdatePlugin)
			self.close()

	def layoutFinished(self):
		self.checkTrafficLight()
		self.rebuildList()

	def UpdatePackageNr(self):
		self.packages = len(self.list)
		print self.packages
		print"packagenr" + str(self.packages)
		self["packagenr"].setText(str(self.packages))
		if self.packages == 0:
			self['key_green'].hide()
			self['key_green_pic'].hide()
		else:
			self['key_green'].show()
			self['key_green_pic'].show()

	def checkTrafficLight(self):
		print"checkTrafficLight"
		from urllib import urlopen
		import socket
		self['a_red'].hide()
		self['a_yellow'].hide()
		self['a_green'].hide()
		self['feedstatusRED'].hide()
		self['feedstatusYELLOW'].hide()
		self['feedstatusGREEN'].hide()
		currentTimeoutDefault = socket.getdefaulttimeout()
		socket.setdefaulttimeout(3)
		try:
			urlOpeneight = "http://feed.openeight.de/status"
			d = urlopen(urlOpeneight)
			self.trafficLight = int(d.read())
			if self.trafficLight == 2:
				self['a_off'].hide()
				self['a_red'].show()
				self['feedstatusRED'].show()
			elif self.trafficLight == 1:
				self['a_off'].hide()
				self['a_yellow'].show()
				self['feedstatusYELLOW'].show()
			elif self.trafficLight == 0:
				self['a_off'].hide()
				self['a_green'].show()
				self['feedstatusGREEN'].show()
		except:
			self.trafficLight = 3
			self['a_off'].show()
		socket.setdefaulttimeout(currentTimeoutDefault)

	def setStatus(self,status = None):
		if status:
			self.statuslist = []
			divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/div-h.png"))
			if status == 'update':
				statuspng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/SoftwareManager/upgrade.png"))
				self.statuslist.append(( _("Package list update"), '', _("Trying to download a new updatelist. Please wait..." ),'',statuspng, divpng ))
			elif status == 'error':
				statuspng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/SoftwareManager/remove.png"))
				self.statuslist.append(( _("Error"), '', _("There was an error downloading the updatelist. Please try again." ),'',statuspng, divpng ))
			elif status == 'noupdate':
				statuspng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/SoftwareManager/installed.png"))
				self.statuslist.append(( _("Nothing to upgrade"), '', _("There are no updates available." ),'',statuspng, divpng ))

			self['list'].setList(self.statuslist)

	def rebuildList(self):
		self.setStatus('update')
		self.ipkg.startCmd(IpkgComponent.CMD_UPDATE)

	def ipkgCallback(self, event, param):
		if event == IpkgComponent.EVENT_ERROR:
			self.setStatus('error')
		elif event == IpkgComponent.EVENT_DONE:
			if self.update == False:
				self.update = True
				self.ipkg.startCmd(IpkgComponent.CMD_UPGRADE_LIST)
			else:
				self.buildPacketList()
		pass
	
	def buildEntryComponent(self, name, version, description, state):
		divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/div-h.png"))
		if not description:
			description = "No description available."
		if state == 'installed':
			installedpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/SoftwareManager/installed.png"))
			return((name, version, _(description), state, installedpng, divpng))	
		elif state == 'upgradeable':
			upgradeablepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/SoftwareManager/upgradeable.png"))
			return((name, version, _(description), state, upgradeablepng, divpng))	
		else:
			installablepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, "SystemPlugins/SoftwareManager/installable.png"))
			return((name, version, _(description), state, installablepng, divpng))

	def buildPacketList(self):
		self.list = []
		fetchedList = self.ipkg.getFetchedList()

		if len(fetchedList) > 0:
			for x in fetchedList:
				try:
					self.list.append(self.buildEntryComponent(x[0], x[1], x[2], "upgradeable"))
				except:
					print "[SOFTWAREPANEL] " + x[0] + " no valid architecture, ignoring !!"

			self['list'].setList(self.list)

		elif len(fetchedList) == 0:
			self.setStatus('noupdate')
		else:
			self.setStatus('error')

		self.UpdatePackageNr()
