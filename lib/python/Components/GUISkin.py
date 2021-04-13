from GUIComponent import GUIComponent
from config import config
from skin import applyAllAttributes
from Tools.CList import CList
from Sources.StaticText import StaticText


class screenPath():
	def __init__(self):
		self.path = []
		self.lastself = None


screen = screenPath()


class GUISkin:
	__module__ = __name__

	def __init__(self):
		self["Title"] = StaticText()
		self["screen_path"] = StaticText()
		self.skin_title = ""
		self.onLayoutFinish = []
		self.summaries = CList()
		self.instance = None
		self.desktop = None
		self.screenPathMode = False

	def createGUIScreen(self, parent, desktop, updateonly=False):
		for val in self.renderer:
			if isinstance(val, GUIComponent):
				if not updateonly:
					val.GUIcreate(parent)
				if not val.applySkin(desktop, self):
					print "warning, skin is missing renderer", val, "in", self

		for key in self:
			val = self[key]
			if isinstance(val, GUIComponent):
				if not updateonly:
					val.GUIcreate(parent)
				depr = val.deprecationInfo
				if val.applySkin(desktop, self):
					if depr:
						print "WARNING: OBSOLETE COMPONENT '%s' USED IN SKIN. USE '%s' INSTEAD!" % (key, depr[0])
						print "OBSOLETE COMPONENT WILL BE REMOVED %s, PLEASE UPDATE!" % (depr[1])
				elif not depr:
					print "warning, skin is missing element", key, "in", self

		for w in self.additionalWidgets:
			if not updateonly:
				w.instance = w.widget(parent)
				# w.instance.thisown = 0
			applyAllAttributes(w.instance, desktop, w.skinAttributes, self.scale)

		for f in self.onLayoutFinish:
			if type(f) is not type(self.close): # is this the best way to do this?
				exec f in globals(), locals()
			else:
				f()

	def deleteGUIScreen(self):
		for (name, val) in self.items():
			if isinstance(val, GUIComponent):
				val.GUIdelete()

	def close(self):
		self.deleteGUIScreen()

	def createSummary(self):
		return None

	def addSummary(self, summary):
		if summary is not None:
			self.summaries.append(summary)

	def removeSummary(self, summary):
		if summary is not None:
			self.summaries.remove(summary)

	def clearScreenPath(self):
		screen.path = []
		screen.lastself = None

	def removeScreenPath(self):
		screen.path = screen.path and screen.path[:-1]
		screen.lastself = None

	def setScreenPathMode(self, mode):
		self.screenPathMode = mode

	def setTitle(self, title):
		path_text = ""
		self.skin_title = title
		if self.screenPathMode is not None and title and config.usage.menu_path.value != "off":
			if self.screenPathMode and not screen.path or screen.path and screen.path[-1] != title:
				self.onClose.append(self.removeScreenPath)
				if screen.lastself != self:
					screen.path.append(title)
					screen.lastself = self
				elif screen.path:
					screen.path[-1] = title
			if config.usage.menu_path.value == "small":
				path_text = len(screen.path) > 1 and " > ".join(screen.path[:-1]) + " >" or ""
			else:
				title = screen.path and " > ".join(screen.path) or title
		if self.instance:
			self.instance.setTitle(title)
		self["Title"].text = title
		self["screen_path"].text = path_text
		self.summaries.setTitle(title)

	def getTitle(self):
		return self.skin_title

	def getSkinTitle(self):
		return hasattr(self, "skin_title") and self.skin_title or ""

	title = property(getTitle, setTitle)

	def setDesktop(self, desktop):
		self.desktop = desktop

	def applySkin(self):
		z = 0
		baseres = (720, 576) # FIXME: a skin might have set another resolution, which should be the base res
		idx = 0
		skin_title_idx = -1
		title = self.title
		for (key, value) in self.skinAttributes:
			if key == "zPosition":
				z = int(value)
			elif key == "title":
				self.skin_title = _(value)
				skin_title_idx = idx
				if title:
					self.skinAttributes[skin_title_idx] = ("title", title)
				else:
					self["Title"].text = self.skin_title
					self.summaries.setTitle(self.skin_title)
			elif key == "baseResolution":
				baseres = tuple([int(x) for x in value.split(',')])
			idx += 1
		self.scale = ((baseres[0], baseres[0]), (baseres[1], baseres[1]))

		if not self.instance:
			from enigma import eWindow
			self.instance = eWindow(self.desktop, z)

		if skin_title_idx == -1 and title:
			self.skinAttributes.append(("title", title))

		# we need to make sure that certain attributes come last
		self.skinAttributes.sort(key=lambda a: {"position": 1}.get(a[0], 0))

		applyAllAttributes(self.instance, self.desktop, self.skinAttributes, self.scale)
		self.createGUIScreen(self.instance, self.desktop)
