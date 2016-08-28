from Screens.Screen import Screen
from Screens.ChannelSelection import *
from Screens.MessageBox import MessageBox
from Tools.BoundFunction import boundFunction
from Components.Sources.StaticText import StaticText
from Components.ActionMap import HelpableActionMap, ActionMap, NumberActionMap
from Components.Label import Label

from Components.config import config, ConfigSubsection, ConfigSelection, ConfigSubList, getConfigListEntry, KEY_LEFT, KEY_RIGHT, KEY_0, ConfigNothing, ConfigPIN, ConfigText, ConfigYesNo, NoSave
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.SystemInfo import SystemInfo
from enigma import eTimer, eDVBCI_UI, eDVBCIInterfaces, eEnv
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.ConfigList import ConfigList
from Components.Label import Label
from Components.SelectionList import SelectionList
from Components.MenuList import MenuList
from Components.Pixmap import Pixmap
from ServiceReference import ServiceReference
from xml.etree.cElementTree import parse as ci_parse
from Tools.XMLTools import elementsWithTag, mergeText, stringToXML
from os import system, path as os_path

MAX_NUM_CI = 4

forceNotShowCiMessages = False

def setCIBitrate(configElement):
	if configElement.value == "no":
		eDVBCI_UI.getInstance().setClockRate(configElement.slotid, eDVBCI_UI.rateNormal)
	else:
		eDVBCI_UI.getInstance().setClockRate(configElement.slotid, eDVBCI_UI.rateHigh)

def InitCiConfig():
	config.ci = ConfigSubList()
	for slot in range(MAX_NUM_CI):
		config.ci.append(ConfigSubsection())
		config.ci[slot].canDescrambleMultipleServices = ConfigSelection(choices = [("auto", _("Auto")), ("no", _("No")), ("yes", _("Yes"))], default = "auto")
		config.ci[slot].use_static_pin = ConfigYesNo(default = True)
		config.ci[slot].static_pin = ConfigPIN(default = 0)
		config.ci[slot].show_ci_messages = ConfigYesNo(default = True)
		if SystemInfo["CommonInterfaceSupportsHighBitrates"]:
			config.ci[slot].canHandleHighBitrates = ConfigSelection(choices = [("no", _("No")), ("yes", _("Yes"))], default = "no")
			config.ci[slot].canHandleHighBitrates.slotid = slot
			config.ci[slot].canHandleHighBitrates.addNotifier(setCIBitrate)

class MMIDialog(Screen):
	def __init__(self, session, slotid, action, handler = eDVBCI_UI.getInstance(), wait_text = "", screen_data = None):
		Screen.__init__(self, session)

		print "MMIDialog with action" + str(action)

		self.mmiclosed = False
		self.tag = None
		self.slotid = slotid

		self.timer = eTimer()
		self.timer.callback.append(self.keyCancel)

		#else the skins fails
		self["title"] = Label("")
		self["subtitle"] = Label("")
		self["bottom"] = Label("")
		self["entries"] = ConfigList([ ])

		self["actions"] = NumberActionMap(["SetupActions", "MenuActions"],
			{
				"ok": self.okbuttonClick,
				"cancel": self.keyCancel,
				"menu": self.forceExit,
				#for PIN
				"left": self.keyLeft,
				"right": self.keyRight,
				"1": self.keyNumberGlobal,
				"2": self.keyNumberGlobal,
				"3": self.keyNumberGlobal,
				"4": self.keyNumberGlobal,
				"5": self.keyNumberGlobal,
				"6": self.keyNumberGlobal,
				"7": self.keyNumberGlobal,
				"8": self.keyNumberGlobal,
				"9": self.keyNumberGlobal,
				"0": self.keyNumberGlobal
			}, -1)

		self.action = action
		self.screen_data = screen_data

		self.is_pin_list = -1
		self.handler = handler
		if wait_text == "":
			self.wait_text = _("wait for ci...")
		else:
			self.wait_text = wait_text

		if action == 2:		#start MMI
			handler.startMMI(self.slotid)
			self.showWait()
		elif action == 3:		#mmi already there (called from infobar)
			self.showScreen()

	def addEntry(self, list, entry):
		if entry[0] == "TEXT":		#handle every item (text / pin only?)
			list.append( (entry[1], ConfigNothing(), entry[2]) )
		if entry[0] == "PIN":
			pinlength = entry[1]
			if entry[3] == 1:
				# masked pins:
				x = ConfigPIN(0, len = pinlength, censor = "*")
			else:
				# unmasked pins:
				x = ConfigPIN(0, len = pinlength)
			x.addEndNotifier(self.pinEntered)
			self["subtitle"].setText(entry[2])
			list.append( getConfigListEntry("", x) )
			self["bottom"].setText(_("please press OK when ready"))

	def pinEntered(self, value):
		self.okbuttonClick()

	def okbuttonClick(self):
		self.timer.stop()
		if not self.tag:
			return
		if self.tag == "WAIT":
			print "do nothing - wait"
		elif self.tag == "MENU":
			print "answer MENU"
			cur = self["entries"].getCurrent()
			if cur:
				self.handler.answerMenu(self.slotid, cur[2])
			else:
				self.handler.answerMenu(self.slotid, 0)
			self.showWait()
		elif self.tag == "LIST":
			print "answer LIST"
			self.handler.answerMenu(self.slotid, 0)
			self.showWait()
		elif self.tag == "ENQ":
			cur = self["entries"].getCurrent()
			answer = str(cur[1].value)
			length = len(answer)
			while length < cur[1].getLength():
				answer = '0' + answer
				length += 1
			self.answer = answer
			if config.ci[self.slotid].use_static_pin.value:
				self.session.openWithCallback(self.save_PIN_CB, MessageBox, _("Would you save the entered PIN %s persistent?") % self.answer, MessageBox.TYPE_YESNO)
			else:
				self.save_PIN_CB(False)

	def save_PIN_CB(self, ret = None):
		if ret:
			config.ci[self.slotid].static_pin.value = self.answer
			config.ci[self.slotid].static_pin.save()
		self.handler.answerEnq(self.slotid, self.answer)
		self.showWait()

	def closeMmi(self):
		self.timer.stop()
		self.close(self.slotid)

	def forceExit(self):
		self.timer.stop()
		if self.tag == "WAIT":
			self.handler.stopMMI(self.slotid)
			global forceNotShowCiMessages
			forceNotShowCiMessages = True
			self.close(self.slotid)

	def keyCancel(self):
		self.timer.stop()
		if not self.tag or self.mmiclosed:
			self.closeMmi()
		elif self.tag == "WAIT":
			self.handler.stopMMI(self.slotid)
			self.closeMmi()
		elif self.tag in ( "MENU", "LIST" ):
			print "cancel list"
			self.handler.answerMenu(self.slotid, 0)
			self.showWait()
		elif self.tag == "ENQ":
			print "cancel enq"
			self.handler.cancelEnq(self.slotid)
			self.showWait()
		else:
			print "give cancel action to ci"

	def keyConfigEntry(self, key):
		self.timer.stop()
		try:
			self["entries"].handleKey(key)
			if self.is_pin_list == 4:
				self.okbuttonClick()
		except:
			pass

	def keyNumberGlobal(self, number):
		self.timer.stop()
		if self.is_pin_list > -1:
			self.is_pin_list += 1
		self.keyConfigEntry(KEY_0 + number)

	def keyLeft(self):
		self.timer.stop()
		if self.is_pin_list > 0:
			self.is_pin_list += -1
		self.keyConfigEntry(KEY_LEFT)

	def keyRight(self):
		self.timer.stop()
		if self.is_pin_list > -1 and self.is_pin_list < 4:
			self.is_pin_list += 1
		self.keyConfigEntry(KEY_RIGHT)

	def updateList(self, list):
		List = self["entries"]
		try:
			List.instance.moveSelectionTo(0)
		except:
			pass
		List.l.setList(list)

	def showWait(self):
		self.tag = "WAIT"
		self["title"].setText("")
		self["subtitle"].setText("")
		self["bottom"].setText("")
		list = [ ]
		list.append( (self.wait_text, ConfigNothing()) )
		self.updateList(list)

	def showScreen(self):
		if self.screen_data is not None:
			screen = self.screen_data
			self.screen_data = None
		else:
			screen = self.handler.getMMIScreen(self.slotid)

		list = [ ]

		self.timer.stop()
		if len(screen) > 0 and screen[0][0] == "CLOSE":
			timeout = screen[0][1]
			self.mmiclosed = True
			if timeout > 0:
				self.timer.start(timeout*1000, True)
			else:
				self.keyCancel()
		else:
			self.mmiclosed = False
			self.tag = screen[0][0]
			for entry in screen:
				if entry[0] == "PIN":
					if config.ci[self.slotid].use_static_pin.value and str(config.ci[self.slotid].static_pin.value) != "0":
						answer = str(config.ci[self.slotid].static_pin.value)
						length = len(answer)
						while length < config.ci[self.slotid].static_pin.getLength():
							answer = '0' + answer
							length += 1
						self.handler.answerEnq(self.slotid, answer)
						self.showWait()
						break
					else:
						self.is_pin_list = 0
						self.addEntry(list, entry)
				else:
					if entry[0] == "TITLE":
						self["title"].setText(entry[1])
					elif entry[0] == "SUBTITLE":
						self["subtitle"].setText(entry[1])
					elif entry[0] == "BOTTOM":
						self["bottom"].setText(entry[1])
					elif entry[0] == "TEXT":
						self.addEntry(list, entry)
			self.updateList(list)

	def ciStateChanged(self):
		do_close = False
		if self.action == 0:			#reset
			do_close = True
		if self.action == 1:			#init
			do_close = True

		#module still there ?
		if self.handler.getState(self.slotid) != 2:
			do_close = True

		#mmi session still active ?
		if self.handler.getMMIState(self.slotid) != 1:
			do_close = True

		if do_close:
			self.closeMmi()
		elif self.action > 1 and self.handler.availableMMI(self.slotid) == 1:
			self.showScreen()

		#FIXME: check for mmi-session closed

class CiMessageHandler:
	def __init__(self):
		self.session = None
		self.auto_close = False
		self.ci = { }
		self.dlgs = { }
		eDVBCI_UI.getInstance().ciStateChanged.get().append(self.ciStateChanged)
		SystemInfo["CommonInterface"] = eDVBCIInterfaces.getInstance().getNumOfSlots() > 0
		try:
			file = open("/proc/stb/tsmux/ci0_tsclk", "r")
			file.close()
			SystemInfo["CommonInterfaceSupportsHighBitrates"] = True
		except:
			SystemInfo["CommonInterfaceSupportsHighBitrates"] = False

	def setSession(self, session):
		self.session = session

	def ciStateChanged(self, slot):
		if slot in self.ci:
			self.ci[slot](slot)
		else:
			handler = eDVBCI_UI.getInstance()
			if slot in self.dlgs:
				self.dlgs[slot].ciStateChanged()
			elif handler.availableMMI(slot) == 1:
				if self.session:
					show_ui = False
					if config.ci[slot].show_ci_messages.value:
						show_ui = True
					screen_data = handler.getMMIScreen(slot)
					if config.ci[slot].use_static_pin.value:
						if screen_data is not None and len(screen_data):
							ci_tag = screen_data[0][0]
							if ci_tag == 'ENQ' and len(screen_data) >= 2 and screen_data[1][0] == 'PIN':
								if str(config.ci[slot].static_pin.value) == "0":
									show_ui = True
								else:
									answer = str(config.ci[slot].static_pin.value)
									length = len(answer)
									while length < config.ci[slot].static_pin.getLength():
										answer = '0' + answer
										length += 1
									handler.answerEnq(slot, answer)
									show_ui = False
									self.auto_close = True
							elif ci_tag == 'CLOSE' and self.auto_close:
								show_ui = False
								self.auto_close = False
					if show_ui and not forceNotShowCiMessages:
						self.dlgs[slot] = self.session.openWithCallback(self.dlgClosed, MMIDialog, slot, 3, screen_data = screen_data)

	def dlgClosed(self, slot):
		if slot in self.dlgs:
			del self.dlgs[slot]

	def registerCIMessageHandler(self, slot, func):
		self.unregisterCIMessageHandler(slot)
		self.ci[slot] = func

	def unregisterCIMessageHandler(self, slot):
		if slot in self.ci:
			del self.ci[slot]

CiHandler = CiMessageHandler()

class CiSelection(Screen):
	def __init__(self, session):
		Screen.__init__(self, session)
		self["actions"] = ActionMap(["OkCancelActions", "CiSelectionActions", "ColorActions"],
			{
				"blue": self.CIAssignment,
				"left": self.keyLeft,
				"right": self.keyLeft,
				"ok": self.okbuttonClick,
				"cancel": self.cancel
			},-1)

		self.dlg = None
		self.state = { }
		self.list = [ ]
		self["key_blue"] = Label(_("CI assignment"))
		self["key_blue"].hide()
		self["pixmap_blue"] = Pixmap()
		self["pixmap_blue"].hide()

		for slot in range(MAX_NUM_CI):
			state = eDVBCI_UI.getInstance().getState(slot)
			if state != -1:
				self.appendEntries(slot, state)
				CiHandler.registerCIMessageHandler(slot, self.ciStateChanged)

		menuList = ConfigList(self.list)
		menuList.list = self.list
		menuList.l.setList(self.list)
		self["entries"] = menuList
		self["entries"].onSelectionChanged.append(self.selectionChanged)
		self["text"] = Label(_("Slot %d")%(1))
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		global forceNotShowCiMessages
		forceNotShowCiMessages = False

	def selectionChanged(self):
		cur_idx = self["entries"].getCurrentIndex()
		self["text"].setText(_("Slot %d")%((cur_idx / 9)+1))

	def keyConfigEntry(self, key):
		try:
			self["entries"].handleKey(key)
			self["entries"].getCurrent()[1].save()
		except:
			pass

	def keyLeft(self):
		self.keyConfigEntry(KEY_LEFT)

	def keyRight(self):
		self.keyConfigEntry(KEY_RIGHT)

	def CIAssignment(self):
		self.session.open(CIselectMainMenu)

	def appendEntries(self, slot, state):
		self.state[slot] = state
		self.list.append((_("Reset"), ConfigNothing(), 0, slot))
		self.list.append((_("Init"), ConfigNothing(), 1, slot))

		if self.state[slot] == 0: #no module
			self["key_blue"].hide()
			self["pixmap_blue"].hide()
			self.list.append((_("no module found"), ConfigNothing(), 2, slot))
		elif self.state[slot] == 1: #module in init
			self["key_blue"].show()
			self["pixmap_blue"].show()
			self.list.append((_("init module"), ConfigNothing(), 2, slot))
		elif self.state[slot] == 2: #module ready
			self["key_blue"].show()
			self["pixmap_blue"].show()
			appname = eDVBCI_UI.getInstance().getAppName(slot)
			self.list.append((appname, ConfigNothing(), 2, slot))
		self.list.append(getConfigListEntry(_("Set pin code persistent"), config.ci[slot].use_static_pin))
		self.list.append((_("Enter persistent PIN code"), ConfigNothing(), 5, slot))
		self.list.append((_("Reset persistent PIN code"), ConfigNothing(), 6, slot))
		self.list.append(getConfigListEntry(_("Show CI messages"), config.ci[slot].show_ci_messages))
		self.list.append(getConfigListEntry(_("Multiple service support"), config.ci[slot].canDescrambleMultipleServices))
		if SystemInfo["CommonInterfaceSupportsHighBitrates"]:
			self.list.append(getConfigListEntry(_("High bitrate support"), config.ci[slot].canHandleHighBitrates))

	def updateState(self, slot):
		state = eDVBCI_UI.getInstance().getState(slot)
		self.state[slot] = state

		slotidx=0
		while len(self.list[slotidx]) < 3 or self.list[slotidx][3] != slot:
			slotidx += 1

		slotidx += 1 #do not change Reset
		slotidx += 1 #do not change Init

		if state == 0: #no module
			self.list[slotidx] = (_("no module found"), ConfigNothing(), 2, slot)
		elif state == 1: #module in init
			self.list[slotidx] = (_("init module"), ConfigNothing(), 2, slot)
		elif state == 2: #module ready
			appname = eDVBCI_UI.getInstance().getAppName(slot)
			self.list[slotidx] = (appname, ConfigNothing(), 2, slot)
		lst = self["entries"]
		lst.list = self.list
		lst.l.setList(self.list)

	def ciStateChanged(self, slot):
		if self.dlg:
			self.dlg.ciStateChanged()
		else:
			state = eDVBCI_UI.getInstance().getState(slot)
			if self.state[slot] != state:
				self.state[slot] = state
				self.updateState(slot)

	def dlgClosed(self, slot):
		self.dlg = None

	def okbuttonClick(self):
		cur = self["entries"].getCurrent()
		if cur and len(cur) > 2:
			action = cur[2]
			slot = cur[3]
			if action == 0: #reset
				eDVBCI_UI.getInstance().setReset(slot)
			elif action == 1: #init
				eDVBCI_UI.getInstance().setInit(slot)
			elif action == 5:
				self.session.openWithCallback(self.cancelCB, PermanentPinEntry, config.ci[slot].static_pin, _("Smartcard PIN"))
			elif action == 6:
				config.ci[slot].static_pin.value = 0
				config.ci[slot].static_pin.save()
				self.session.openWithCallback(self.cancelCB, MessageBox, _("The saved PIN was cleared."), MessageBox.TYPE_INFO)
			elif self.state[slot] == 2:
				self.dlg = self.session.openWithCallback(self.dlgClosed, MMIDialog, slot, action)

	def cancelCB(self, value):
		pass

	def cancel(self):
		for slot in range(MAX_NUM_CI):
			state = eDVBCI_UI.getInstance().getState(slot)
			if state != -1:
				CiHandler.unregisterCIMessageHandler(slot)
		self.close()

class PermanentPinEntry(Screen, ConfigListScreen):
	def __init__(self, session, pin, pin_slot):
		Screen.__init__(self, session)
		self.skinName = ["ParentalControlChangePin", "Setup" ]
		self.setup_title = _("Enter pin code")
		self.onChangedEntry = [ ]

		self.slot = pin_slot
		self.pin = pin
		self.list = []
		self.pin1 = ConfigPIN(default = 0, censor = "*")
		self.pin2 = ConfigPIN(default = 0, censor = "*")
		self.pin1.addEndNotifier(boundFunction(self.valueChanged, 1))
		self.pin2.addEndNotifier(boundFunction(self.valueChanged, 2))
		self.list.append(getConfigListEntry(_("Enter PIN"), NoSave(self.pin1)))
		self.list.append(getConfigListEntry(_("Reenter PIN"), NoSave(self.pin2)))
		ConfigListScreen.__init__(self, self.list)

		self["actions"] = NumberActionMap(["DirectionActions", "ColorActions", "OkCancelActions"],
		{
			"cancel": self.cancel,
			"red": self.cancel,
			"save": self.keyOK,
		}, -1)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("OK"))
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.setTitle(self.setup_title)

	def valueChanged(self, pin, value):
		if pin == 1:
			self["config"].setCurrentIndex(1)
		elif pin == 2:
			self.keyOK()

	def keyOK(self):
		if self.pin1.value == self.pin2.value:
			self.pin.value = self.pin1.value
			self.pin.save()
			self.session.openWithCallback(self.close, MessageBox, _("The PIN code has been saved successfully."), MessageBox.TYPE_INFO)
		else:
			self.session.open(MessageBox, _("The PIN codes you entered are different."), MessageBox.TYPE_ERROR)

	def cancel(self):
		self.close(None)

	def keyNumberGlobal(self, number):
		ConfigListScreen.keyNumberGlobal(self, number)

	def changedEntry(self):
		for x in self.onChangedEntry:
			x()

	def getCurrentEntry(self):
		return self["config"].getCurrent()[0]

	def getCurrentValue(self):
		return str(self["config"].getCurrent()[1].getText())

	def createSummary(self):
		from Screens.Setup import SetupSummary
		return SetupSummary

class CIselectMainMenu(Screen):
	skin = """
		<screen name="CIselectMainMenu" position="center,center" size="500,250" title="CI assignment" >
			<widget name="CiList" position="5,0" size="490,200" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session, args = 0):

		Screen.__init__(self, session)

		self["actions"] = ActionMap(["ColorActions","SetupActions"],
			{
				"ok": self.greenPressed,
				"cancel": self.close
			}, -1)

		NUM_CI=eDVBCIInterfaces.getInstance().getNumOfSlots()

		print "[CI_Wizzard] FOUND %d CI Slots " % NUM_CI

		self.dlg = None
		self.state = { }
		self.list = [ ]
		if NUM_CI > 0:
			for slot in range(NUM_CI):
				state = eDVBCI_UI.getInstance().getState(slot)
				if state != -1:
					if  state == 1:
						appname = _("Slot %d") %(slot+1) + " - " + _("init modules")
					elif state == 2:
						appname = _("Slot %d") %(slot+1) + " - " + eDVBCI_UI.getInstance().getAppName(slot)
					self.list.append( (appname, ConfigNothing(), 0, slot) )
		else:
			self.list.append( (_("no CI slots found") , ConfigNothing(), 1, -1) )

		menuList = ConfigList(self.list)
		menuList.list = self.list
		menuList.l.setList(self.list)
		self["CiList"] = menuList
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_("CI assignment"))

	def greenPressed(self):
		cur = self["CiList"].getCurrent()
		if cur and len(cur) > 2:
			action = cur[2]
			slot = cur[3]
			if action == 1:
				print "[CI_Wizzard] there is no CI Slot in your %s" % slot 
			else:
				print "[CI_Wizzard] selected CI Slot : %d" % slot
				if config.usage.setup_level.index > 1: # advanced
					self.session.open(CIconfigMenu, slot)
				else:
					self.session.open(easyCIconfigMenu, slot)

				
        """def yellowPressed(self): # unused
		NUM_CI=eDVBCIInterfaces.getInstance().getNumOfSlots()
		print "[CI_Check] FOUND %d CI Slots " % NUM_CI
		if NUM_CI > 0:
			for ci in range(NUM_CI):
				print eDVBCIInterfaces.getInstance().getDescrambleRules(ci)"""


class CIconfigMenu(Screen):
	skin = """
		<screen name="CIconfigMenu" position="center,center" size="560,440" title="CI assignment" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget source="CAidList_desc" render="Label" position="5,50" size="550,22" font="Regular;20"  backgroundColor="#25062748" transparent="1" />
			<widget source="CAidList" render="Label" position="5,80" size="550,45" font="Regular;20"  backgroundColor="#25062748" transparent="1" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,125" zPosition="1" size="560,2" />
			<widget source="ServiceList_desc" render="Label" position="5,130" size="550,22" font="Regular;20" backgroundColor="#25062748" transparent="1"  />
			<widget name="ServiceList" position="5,160" size="550,250" zPosition="1" scrollbarMode="showOnDemand" />
			<widget source="ServiceList_info" render="Label" position="5,160" size="550,250" zPosition="2" font="Regular;20" backgroundColor="#25062748" transparent="1"  />
		</screen>"""

	def __init__(self, session, ci_slot="9"):

		Screen.__init__(self, session)
		self.ci_slot=ci_slot
		self.filename = eEnv.resolve("${sysconfdir}/enigma2/ci") + str(self.ci_slot) + ".xml"

		self["key_red"] = StaticText(_("Delete"))
		self["key_green"] = StaticText(_("Add service"))
		self["key_yellow"] = StaticText(_("Add provider"))
		self["key_blue"] = StaticText(_("Select CAId"))
		self["CAidList_desc"] = StaticText(_("Assigned CAIds:"))
		self["CAidList"] = StaticText()
		self["ServiceList_desc"] = StaticText(_("Assigned services/provider:"))
		self["ServiceList_info"] = StaticText()

		self["actions"] = ActionMap(["ColorActions","SetupActions"],
			{
				"green": self.greenPressed,
				"red": self.redPressed,
				"yellow": self.yellowPressed,
				"blue": self.bluePressed,
				"cancel": self.cancel
			}, -1)

		print "[CI_Wizzard_Config] Configuring CI Slots : %d  " % self.ci_slot

		i=0
		self.caidlist=[]
		print eDVBCIInterfaces.getInstance().readCICaIds(self.ci_slot)
		for caid in eDVBCIInterfaces.getInstance().readCICaIds(self.ci_slot):
			i+=1
			self.caidlist.append((str(hex(int(caid))),str(caid),i))

		print "[CI_Wizzard_Config_CI%d] read following CAIds from CI: %s" %(self.ci_slot, self.caidlist)

		self.selectedcaid = []
		self.servicelist = []
		self.caids = ""

		serviceList = ConfigList(self.servicelist)
		serviceList.list = self.servicelist
		serviceList.l.setList(self.servicelist)
		self["ServiceList"] = serviceList

		self.loadXML()
		# if config mode !=advanced autoselect any caid
		if config.usage.setup_level.index <= 1: # advanced
			self.selectedcaid=self.caidlist
			self.finishedCAidSelection(self.selectedcaid)
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_("CI assignment"))

	def redPressed(self):
		self.delete()

	def greenPressed(self):
		self.session.openWithCallback( self.finishedChannelSelection, myChannelSelection, None)

	def yellowPressed(self):
		self.session.openWithCallback( self.finishedProviderSelection, myProviderSelection, None)

	def bluePressed(self):
		self.session.openWithCallback(self.finishedCAidSelection, CAidSelect, self.caidlist, self.selectedcaid)

	def cancel(self):
		self.saveXML()
		activate_all(self)
		self.close()

	def setServiceListInfo(self):
		if len(self.servicelist):
			self["ServiceList_info"].setText("")
		else:
			self["ServiceList_info"].setText(_("No services/providers selected"))

	def delete(self):
		cur = self["ServiceList"].getCurrent()
		if cur and len(cur) > 2:
			self.servicelist.remove(cur)
		self["ServiceList"].l.setList(self.servicelist)
		self.setServiceListInfo()

	def finishedChannelSelection(self, *args):
		if len(args):
			ref=args[0]
			service_ref = ServiceReference(ref)
			service_name = service_ref.getServiceName()
			if find_in_list(self.servicelist, service_name, 0)==False:
				split_ref=service_ref.ref.toString().split(":")
				if split_ref[0] == "1":#== dvb service und nicht muell von None
					self.servicelist.append( (service_name , ConfigNothing(), 0, service_ref.ref.toString()) )
					self["ServiceList"].l.setList(self.servicelist)
					self.setServiceListInfo()

	def finishedProviderSelection(self, *args):
		if len(args)>1: # bei nix selected kommt nur 1 arg zurueck (==None)
			name=args[0]
			dvbnamespace=args[1]
			if find_in_list(self.servicelist, name, 0)==False:
				self.servicelist.append( (name , ConfigNothing(), 1, dvbnamespace) )
				self["ServiceList"].l.setList(self.servicelist)
				self.setServiceListInfo()

	def finishedCAidSelection(self, *args):
		if len(args):
			self.selectedcaid=args[0]
			self.caids=""
			if len(self.selectedcaid):
				for item in self.selectedcaid:
					if len(self.caids):
						self.caids+= ", " + item[0]
					else:
						self.caids=item[0]
			else:
				self.selectedcaid=[]
				self.caids=_("no CAId selected")
		else:
			self.selectedcaid=[]
			self.caids=_("no CAId selected")
		self["CAidList"].setText(self.caids)

	def saveXML(self):
		try:
			fp = open(self.filename, 'w')
			fp.write("<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n")
			fp.write("<ci>\n")
			fp.write("\t<slot>\n")
			fp.write("\t\t<id>%s</id>\n" % self.ci_slot)
			for item in self.selectedcaid:
				if len(self.selectedcaid):
					fp.write("\t\t<caid id=\"%s\" />\n" % item[0])
			for item in self.servicelist:
				if len(self.servicelist):
					if item[2]==1:
						fp.write("\t\t<provider name=\"%s\" dvbnamespace=\"%s\" />\n" % (item[0], item[3]))
					else:
						fp.write("\t\t<service name=\"%s\" ref=\"%s\" />\n"  % (item[0], item[3]))
			fp.write("\t</slot>\n")
			fp.write("</ci>\n")
			fp.close()
		except:
			print "[CI_Config_CI%d] xml not written" %self.ci_slot
			os.unlink(self.filename)

	def loadXML(self):
		if not os_path.exists(self.filename):
			return

		def getValue(definitions, default):
			ret = ""
			Len = len(definitions)
			return Len > 0 and definitions[Len-1].text or default

		self.read_services=[]
		self.read_providers=[]
		self.usingcaid=[]
		self.ci_config=[]

		try:
			fp = open(self.filename, 'r')
			tree = ci_parse(fp).getroot()
			fp.close()
			for slot in tree.findall("slot"):
				read_slot = getValue(slot.findall("id"), False).encode("UTF-8")
				print "ci " + read_slot

				i=0
				for caid in slot.findall("caid"):
					read_caid = caid.get("id").encode("UTF-8")
					self.selectedcaid.append((str(read_caid),str(read_caid),i))
					self.usingcaid.append(long(read_caid,16))
					i+=1

				for service in  slot.findall("service"):
					read_service_name = service.get("name").encode("UTF-8")
					read_service_ref = service.get("ref").encode("UTF-8")
					self.read_services.append (read_service_ref)

				for provider in  slot.findall("provider"):
					read_provider_name = provider.get("name").encode("UTF-8")
					read_provider_dvbname = provider.get("dvbnamespace").encode("UTF-8")
					self.read_providers.append((read_provider_name,read_provider_dvbname))

				self.ci_config.append((int(read_slot), (self.read_services, self.read_providers, self.usingcaid)))
		except:
			print "[CI_Config_CI%d] error parsing xml..." %self.ci_slot

		for item in self.read_services:
			if len(item):
				self.finishedChannelSelection(item)

		for item in self.read_providers:
			if len(item):
				self.finishedProviderSelection(item[0],item[1])

		print self.ci_config
		self.finishedCAidSelection(self.selectedcaid)
		self["ServiceList"].l.setList(self.servicelist)
		self.setServiceListInfo()


class easyCIconfigMenu(CIconfigMenu):
	skin = """
		<screen name="easyCIconfigMenu" position="center,center" size="560,440" title="CI assignment" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget source="ServiceList_desc" render="Label" position="5,50" size="550,22" font="Regular;20" backgroundColor="#25062748" transparent="1"  />
			<widget name="ServiceList" position="5,80" size="550,300" zPosition="1" scrollbarMode="showOnDemand" />
			<widget source="ServiceList_info" render="Label" position="5,80" size="550,300" zPosition="2" font="Regular;20" backgroundColor="#25062748" transparent="1"  />
		</screen>"""

	def __init__(self, session, ci_slot="9"):
		Screen.setTitle(self, _("CI assignment"))

		ci=ci_slot
		CIconfigMenu.__init__(self, session, ci_slot)

		self["actions"] = ActionMap(["ColorActions","SetupActions"],
		{
			"green": self.greenPressed,
			"red": self.redPressed,
			"yellow": self.yellowPressed,
			"cancel": self.cancel
		})


class CAidSelect(Screen):
	skin = """
		<screen name="CAidSelect" position="center,center" size="450,440" title="select CAId's" >
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="list" position="5,50" size="440,330" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,390" zPosition="1" size="450,2" />
			<widget source="introduction" render="Label" position="0,400" size="450,40" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />
		</screen>"""

	def __init__(self, session, list, selected_caids):

		Screen.__init__(self, session)

		self.list = SelectionList()
		self["list"] = self.list

		for listindex in range(len(list)):
			if find_in_list(selected_caids,list[listindex][0],0):
				self.list.addSelection(list[listindex][0], list[listindex][1], listindex, True)
			else:
				self.list.addSelection(list[listindex][0], list[listindex][1], listindex, False)

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["introduction"] = StaticText(_("Press OK to select/deselect a CAId."))

		self["actions"] = ActionMap(["ColorActions","SetupActions"],
		{
			"ok": self.list.toggleSelection,
			"cancel": self.cancel,
			"green": self.greenPressed,
			"red": self.cancel
		}, -1)
		self.onShown.append(self.setWindowTitle)

	def setWindowTitle(self):
		self.setTitle(_("select CAId's"))

	def greenPressed(self):
		list = self.list.getSelectionsList()
		print list
		self.close(list)

	def cancel(self):
		self.close()

class myProviderSelection(ChannelSelectionBase):
	skin = """
		<screen name="myProviderSelection" position="center,center" size="560,440" title="Select provider to add...">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget name="list" position="5,50" size="550,330" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,390" zPosition="1" size="560,2" />
			<widget source="introduction" render="Label" position="0,400" size="560,40" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />
		</screen>"""

	def __init__(self, session, title):
		ChannelSelectionBase.__init__(self, session)
		self.onShown.append(self.__onExecCallback)

		self["actions"] = ActionMap(["OkCancelActions", "ChannelSelectBaseActions"],
			{
				"showFavourites": self.doNothing,
				"showAllServices": self.cancel,
				"showProviders": self.doNothing,
				"showSatellites": self.doNothing,
				"cancel": self.cancel,
				"ok": self.channelSelected
			})
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText()
		self["key_yellow"] = StaticText()
		self["key_blue"] = StaticText()
		self["introduction"] = StaticText(_("Press OK to select a provider."))

	def doNothing(self):
		pass

	def __onExecCallback(self):
		self.showSatellites()
		self.setTitle(_("Select provider to add..."))

	def channelSelected(self): # just return selected service
		ref = self.getCurrentSelection()
		splited_ref=ref.toString().split(":")
		if ref.flags == 7 and splited_ref[6] != "0":
			self.dvbnamespace=splited_ref[6]
			self.enterPath(ref)
		else:
			self.close(ref.getName(), self.dvbnamespace)

	def showSatellites(self):
		if not self.pathChangeDisabled:
			refstr = '%s FROM SATELLITES ORDER BY satellitePosition'%(self.service_types)
			if not self.preEnterPath(refstr):
				ref = eServiceReference(refstr)
				justSet=False
				prev = None

				if self.isBasePathEqual(ref):
					if self.isPrevPathEqual(ref):
						justSet=True
					prev = self.pathUp(justSet)
				else:
					currentRoot = self.getRoot()
					if currentRoot is None or currentRoot != ref:
						justSet=True
						self.clearPath()
						self.enterPath(ref, True)
				if justSet:
					serviceHandler = eServiceCenter.getInstance()
					servicelist = serviceHandler.list(ref)
					if not servicelist is None:
						while True:
							service = servicelist.getNext()
							if not service.valid(): #check if end of list
								break
							unsigned_orbpos = service.getUnsignedData(4) >> 16
							orbpos = service.getData(4) >> 16
							if orbpos < 0:
								orbpos += 3600
							if service.getPath().find("FROM PROVIDER") != -1:
								service_type = _("Providers")
								try:
									# why we need this cast?
									service_name = str(nimmanager.getSatDescription(orbpos))
								except:
									if unsigned_orbpos == 0xFFFF: #Cable
										service_name = _("Cable")
									elif unsigned_orbpos == 0xEEEE: #Terrestrial
										service_name = _("Terrestrial")
									else:
										if orbpos > 1800: # west
											orbpos = 3600 - orbpos
											h = _("W")
										else:
											h = _("E")
										service_name = ("%d.%d" + h) % (orbpos / 10, orbpos % 10)
								service.setName("%s - %s" % (service_name, service_type))
								self.servicelist.addService(service)
						self.servicelist.finishFill()
						if prev is not None:
							self.setCurrentSelection(prev)

	def cancel(self):
		self.close(None)

class myChannelSelection(ChannelSelectionBase):
	skin = """
		<screen name="myChannelSelection" position="center,center" size="560,440" title="Select service to add...">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget source="key_green" render="Label" position="140,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget source="key_blue" render="Label" position="420,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
			<widget name="list" position="5,50" size="550,330" scrollbarMode="showOnDemand" />
			<ePixmap pixmap="skin_default/div-h.png" position="0,390" zPosition="1" size="560,2" />
			<widget source="introduction" render="Label" position="0,400" size="560,40" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />
		</screen>"""

	def __init__(self, session, title):
		ChannelSelectionBase.__init__(self, session)
		self.onShown.append(self.__onExecCallback)

		self["actions"] = ActionMap(["OkCancelActions", "TvRadioActions", "ChannelSelectBaseActions"],
			{
				"showProviders": self.doNothing,
				"showSatellites": self.showAllServices,
				"showAllServices": self.cancel,
				"cancel": self.cancel,
				"ok": self.channelSelected,
				"keyRadio": self.setModeRadio,
				"keyTV": self.setModeTv
			})

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("All"))
		self["key_yellow"] = StaticText()
		self["key_blue"] = StaticText(_("Favourites"))
		self["introduction"] = StaticText(_("Press OK to select a provider."))

	def __onExecCallback(self):
		self.setModeTv()
		self.setTitle(_("Select service to add..."))

	def doNothing(self):
		pass

	def channelSelected(self): # just return selected service
		ref = self.getCurrentSelection()
		if (ref.flags & 7) == 7:
			self.enterPath(ref)
		elif not (ref.flags & eServiceReference.isMarker):
			ref = self.getCurrentSelection()
			self.close(ref)

	def setModeTv(self):
		self.setTvMode()
		self.showFavourites()

	def setModeRadio(self):
		self.setRadioMode()
		self.showFavourites()

	def cancel(self):
		self.close(None)

def activate_all(session):
	NUM_CI=eDVBCIInterfaces.getInstance().getNumOfSlots()
	print "[CI_Activate] FOUND %d CI Slots " % NUM_CI
	if NUM_CI > 0:
		ci_config=[]
		def getValue(definitions, default):
			# Initialize Output
			ret = ""
			# How many definitions are present
			Len = len(definitions)
			return Len > 0 and definitions[Len-1].text or default

		for ci in range(NUM_CI):
			filename = eEnv.resolve("${sysconfdir}/enigma2/ci") + str(ci) + ".xml"

			if not os_path.exists(filename):
				print "[CI_Activate_Config_CI%d] no config file found" %ci

			try:
				if not os_path.exists(self.filename):
					return

				fp = open(filename, 'r')
				tree = ci_parse(fp).getroot()
				fp.close()
				read_services=[]
				read_providers=[]
				usingcaid=[]
				for slot in tree.findall("slot"):
					read_slot = getValue(slot.findall("id"), False).encode("UTF-8")

					for caid in slot.findall("caid"):
						read_caid = caid.get("id").encode("UTF-8")
						usingcaid.append(long(read_caid,16))

					for service in slot.findall("service"):
						read_service_ref = service.get("ref").encode("UTF-8")
						read_services.append (read_service_ref)

					for provider in slot.findall("provider"):
						read_provider_name = provider.get("name").encode("UTF-8")
						read_provider_dvbname = provider.get("dvbnamespace").encode("UTF-8")
						read_providers.append((read_provider_name,long(read_provider_dvbname,16)))

					ci_config.append((int(read_slot), (read_services, read_providers, usingcaid)))
			except:
				print "[CI_Activate_Config_CI%d] error parsing xml..." %ci

		for item in ci_config:
			print "[CI_Activate] activate CI%d with following settings:" %item[0]
			print item[0]
			print item[1]
			try:
				eDVBCIInterfaces.getInstance().setDescrambleRules(item[0],item[1])
			except:
				print "[CI_Activate_Config_CI%d] error setting DescrambleRules..." %item[0]

def find_in_list(list, search, listpos=0):
	for item in list:
		if item[listpos]==search:
			return True
	return False
