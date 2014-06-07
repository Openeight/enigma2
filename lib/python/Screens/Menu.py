######################################################
# This python script includes amendment by           #
# pcd@et-view-support January 2014 to the original   #
# openpli 4 Menu.py under the original Licence.      #
# You may freely modify and distribute this          #
# amendment provided you  keep this Licence.         #
######################################################
from Screen import Screen
from Components.Sources.List import List
from Components.ActionMap import NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.config import configfile
from Components.PluginComponent import plugins
from Components.config import config
from Components.SystemInfo import SystemInfo

from Tools.BoundFunction import boundFunction
from Tools.Directories import resolveFilename, SCOPE_SKIN

import xml.etree.cElementTree

from Screens.Setup import Setup, getSetupTitle
################# pcd ########################
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Sources.StaticText import StaticText
import os
from Components.Button import Button
#################pcd end #####################

# read the menu
mdom = xml.etree.cElementTree.parse(resolveFilename(SCOPE_SKIN, 'menu.xml'))

class MenuUpdater:
	def __init__(self):
		self.updatedMenuItems = {}

	def addMenuItem(self, id, pos, text, module, screen, weight):
		if not self.updatedMenuAvailable(id):
			self.updatedMenuItems[id] = []
		self.updatedMenuItems[id].append([text, pos, module, screen, weight])

	def delMenuItem(self, id, pos, text, module, screen, weight):
		self.updatedMenuItems[id].remove([text, pos, module, screen, weight])

	def updatedMenuAvailable(self, id):
		return self.updatedMenuItems.has_key(id)

	def getUpdatedMenu(self, id):
		return self.updatedMenuItems[id]

menuupdater = MenuUpdater()

class MenuSummary(Screen):
	pass

class Menu(Screen):
	ALLOW_SUSPEND = True

	def okbuttonClick(self):
		print "okbuttonClick"
		selection = self["menu"].getCurrent()
		if selection is not None:
			selection[1]()

	def execText(self, text):
		exec text

	def runScreen(self, arg):
		# arg[0] is the module (as string)
		# arg[1] is Screen inside this module
		#        plus possible arguments, as
		#        string (as we want to reference
		#        stuff which is just imported)
		# FIXME. somehow
		if arg[0] != "":
			exec "from " + arg[0] + " import *"

		self.openDialog(*eval(arg[1]))

	def nothing(self): #dummy
		pass

	def openDialog(self, *dialog):				# in every layer needed
		self.session.openWithCallback(self.menuClosed, *dialog)

	def openSetup(self, dialog):
		self.session.openWithCallback(self.menuClosed, Setup, dialog)

	def addMenu(self, destList, node):
		requires = node.get("requires")
		if requires:
			if requires[0] == '!':
				if SystemInfo.get(requires[1:], False):
					return
			elif not SystemInfo.get(requires, False):
				return
		MenuTitle = _(node.get("text", "??").encode("UTF-8"))
		entryID = node.get("entryID", "undefined")
		weight = node.get("weight", 50)
		x = node.get("flushConfigOnClose")
		if x:
			a = boundFunction(self.session.openWithCallback, self.menuClosedWithConfigFlush, Menu, node)
		else:
			a = boundFunction(self.session.openWithCallback, self.menuClosed, Menu, node)
		#TODO add check if !empty(node.childNodes)
		destList.append((MenuTitle, a, entryID, weight))

	def menuClosedWithConfigFlush(self, *res):
		configfile.save()
		self.menuClosed(*res)

	def menuClosed(self, *res):
		if res and res[0]:
			self.close(True)

	def addItem(self, destList, node):
		requires = node.get("requires")
		if requires:
			if requires[0] == '!':
				if SystemInfo.get(requires[1:], False):
					return
			elif not SystemInfo.get(requires, False):
				return
		configCondition = node.get("configcondition")
		if configCondition and not eval(configCondition + ".value"):
			return
		item_text = node.get("text", "").encode("UTF-8")
		entryID = node.get("entryID", "undefined")
		weight = node.get("weight", 50)
		for x in node:
			if x.tag == 'screen':
				module = x.get("module")
				screen = x.get("screen")

				if screen is None:
					screen = module

				print module, screen
				if module:
					module = "Screens." + module
				else:
					module = ""

				# check for arguments. they will be appended to the
				# openDialog call
				args = x.text or ""
				screen += ", " + args

				destList.append((_(item_text or "??"), boundFunction(self.runScreen, (module, screen)), entryID, weight))
				return
			elif x.tag == 'code':
				destList.append((_(item_text or "??"), boundFunction(self.execText, x.text), entryID, weight))
				return
			elif x.tag == 'setup':
				id = x.get("id")
				if item_text == "":
					item_text = _(getSetupTitle(id))
				else:
					item_text = _(item_text)
				destList.append((item_text, boundFunction(self.openSetup, id), entryID, weight))
				return
		destList.append((item_text, self.nothing, entryID, weight))


	def __init__(self, session, parent):
		Screen.__init__(self, session)

		list = []

		menuID = None
		for x in parent:						#walk through the actual nodelist
			if not x.tag:
				continue
			if x.tag == 'item':
				item_level = int(x.get("level", 0))
				if item_level <= config.usage.setup_level.index:
					self.addItem(list, x)
					count += 1
			elif x.tag == 'menu':
				self.addMenu(list, x)
				count += 1
			elif x.tag == "id":
				menuID = x.get("val")
				count = 0

			if menuID is not None:
				# menuupdater?
				if menuupdater.updatedMenuAvailable(menuID):
					for x in menuupdater.getUpdatedMenu(menuID):
						if x[1] == count:
							list.append((x[0], boundFunction(self.runScreen, (x[2], x[3] + ", ")), x[4]))
							count += 1

		if menuID is not None:
			# plugins
			for l in plugins.getPluginsForMenu(menuID):
				# check if a plugin overrides an existing menu
				plugin_menuid = l[2]
				for x in list:
					if x[2] == plugin_menuid:
						list.remove(x)
						break
				list.append((l[0], boundFunction(l[1], self.session, close=self.close), l[2], l[3] or 50))

		# for the skin: first try a menu_<menuID>, then Menu
########################## pcd #################################		
#		self.skinName = [ ]
#		if menuID is not None:
#			self.skinName.append("menu_" + menuID)
#		self.skinName.append("Menu")

		# Sort by Weight
#		list.sort(key=lambda x: int(x[3]))
		self.skinName = [ ]
		self.menuID = menuID
		skfile = "/usr/share/enigma2/" + config.skin.primary_skin.value 
                f1 = file(skfile, "r")
                self.sktxt = f1.read()
                f1.close()    	
                if menuID is not None:
                    if ('<screen name="Animmain" ' in self.sktxt) and (config.usage.mainmenu_mode.value == "horzanim"): 
                        self.skinName.append("Animmain")
                        title = self.menuID
                        self.setTitle(title)
                    elif ('<screen name="Iconmain" ' in self.sktxt) and (config.usage.mainmenu_mode.value == "horzicon"): 
                        self.skinName.append("Iconmain")
                        title = self.menuID
                        self.setTitle(title)
                    else:
                        self.skinName.append("menu_" + menuID)
                self.skinName.append("Menu")


		# Sort by Weight
		list.sort(key=lambda x: int(x[3]))

		self.tlist = list
########################## pcd end #############################
		self["menu"] = List(list)

		self["actions"] = NumberActionMap(["OkCancelActions", "MenuActions", "NumberActions"],
			{
				"ok": self.okbuttonClick,
				"cancel": self.closeNonRecursive,
				"menu": self.closeRecursive,
				"1": self.keyNumberGlobal,
				"2": self.keyNumberGlobal,
				"3": self.keyNumberGlobal,
				"4": self.keyNumberGlobal,
				"5": self.keyNumberGlobal,
				"6": self.keyNumberGlobal,
				"7": self.keyNumberGlobal,
				"8": self.keyNumberGlobal,
				"9": self.keyNumberGlobal
			})

		a = parent.get("title", "").encode("UTF-8") or None
		a = a and _(a)
		if a is None:
			a = _(parent.get("text", "").encode("UTF-8"))
		self["title"] = StaticText(a)
		self.menu_title = a
###################### pcd ###############
                if ('<screen name="Animmain" ' in self.sktxt) and (config.usage.mainmenu_mode.value == "horzanim"): 
                        self.onShown.append(self.openTestA)
                elif ('<screen name="Iconmain" ' in self.sktxt) and (config.usage.mainmenu_mode.value == "horzicon"): 
                        self.onShown.append(self.openTestB)
		
        def openTestA(self):
                 self.session.open(AnimMain, self.tlist, self.menu_title) 
                 self.close()

        def openTestB(self):
                 self.session.open(IconMain, self.tlist, self.menu_title) 
                 self.close()

###################### pcd end #############

	def keyNumberGlobal(self, number):
		print "menu keyNumber:", number
		# Calculate index
		number -= 1

		if len(self["menu"].list) > number:
			self["menu"].setIndex(number)
			self.okbuttonClick()

	def closeNonRecursive(self):
		self.close(False)

	def closeRecursive(self):
		self.close(True)

	def createSummary(self):
		return MenuSummary
		
##################### pcd ###################
class AnimMain(Screen):

	def __init__(self, session, tlist, menuTitle):
		Screen.__init__(self, session)
		self.skinName = "Animmain"
                self.tlist = tlist
                ipage = 1
                list = []
                
                print "tlist =", tlist
                print "menuTitle =", menuTitle
		nopic = len(tlist)
		
                self.pos = []
		self.index = 0
		
		title = menuTitle
		self["title"] = Button(title)
		
		list = []
		tlist = []

                self["label1"] = StaticText()
                self["label2"] = StaticText()
                self["label3"] = StaticText()
                self["label4"] = StaticText()
                self["label5"] = StaticText()
                
        
		self["red"] = Button(_("Exit"))
		self["green"] = Button(_("Select"))
		self["yellow"] = Button(_("Config"))
                		
		self["actions"] = NumberActionMap(["OkCancelActions", "MenuActions", "DirectionActions", "NumberActions", "ColorActions"],
			{
				"ok": self.okbuttonClick,
				"cancel": self.closeNonRecursive,
				"left": self.key_left,
			        "right": self.key_right,
			        "up": self.key_up,
			        "down": self.key_down,
                                "red": self.cancel,
			        "green": self.okbuttonClick,
			        "yellow": self.key_menu,
				"menu": self.closeRecursive,
				"1": self.keyNumberGlobal,
				"2": self.keyNumberGlobal,
				"3": self.keyNumberGlobal,
				"4": self.keyNumberGlobal,
				"5": self.keyNumberGlobal,
				"6": self.keyNumberGlobal,
				"7": self.keyNumberGlobal,
				"8": self.keyNumberGlobal,
				"9": self.keyNumberGlobal
			})
###########################
                nop = len(self.tlist)
                self.nop = nop
                nh = 1
                if nop == 1:
                      nh = 1
                elif nop == 2:
                      nh = 2 
                elif nop == 3:
                      nh = 2
                elif nop == 4:
                      nh = 3
                elif nop == 5:
                      nh = 3
                else:                              
                      nh = int(float(nop)/2)
                print "nop, nh =", nop, nh 
                self.index = nh

###########################

                i = 0
 
                self.onShown.append(self.openTest)



        def key_menu(self):
                return
                
        def cancel(self):
                self.close()
                      
        def paintFrame(self):
                pass

        def getname(self, name):
                        print "Here in getname name =", name
                        if "AutoBouquetsMaker" in name:
                                name = "AutoBouquets\nMakerProvider" 
                        if len(name) > 14:
                            if ("-" in name) or ("/" in name) or (" " in name):
                                name = name.replace("-", "\n-")
                                name = name.replace(" /", "/")
                                name = name.replace("/ ", "/")
                                name = name.replace(" ", "\n")
                            else:
                                name = name[:14] + "\n-" + name[12:]    
                        if "A/V" not in name:
                                name = name.replace("/", "\n")
                        if "di\n" in name:
                                name = name.replace("di\n", "di ")
                        if "de\n" in name:
                                name = name.replace("de\n", "de ")  
                        if "la\n" in name:
                                name = name.replace("la\n", "la ")                        
                        return name
                        
        def openTest(self):
                        print "Here in openTest self.tlist =", self.tlist
                        i = self.index
                        print "Here in openTest i =", i
                        if (i-3) > -1:
                               name1 = self.getname(self.tlist[i-3][0])
                        else:       
                               name1 = " "
                        print "Here in name1 =", name1      
                        if (i-2) > -1:       
                               name2 = self.getname(self.tlist[i-2][0])
                        else:       
                               name2 = " " 
                        print "Here in name2 =", name2       
                        name3 = self.getname(self.tlist[i-1][0])
                        print "Here in name3 =", name3
                        if i < self.nop:
                               name4 = self.getname(self.tlist[i][0])
                        else:       
                               name4 = " "
                        print "Here in name4 =", name4       
                        if (i+1) < self.nop:               
                               name5 = self.getname(self.tlist[i+1][0])
                        else:       
                               name5 = " "
                        print "Here in name5 =", name5
                        self["label1"].setText(name1)
                        self["label2"].setText(name2)
                        self["label3"].setText(name3)
                        self["label4"].setText(name4)
                        self["label5"].setText(name5)

        def key_left(self):
                self.index -= 1
                if self.index < 1:
                       self.index = 1
		       return
		else:
		       self.openTest()

        def key_right(self):
		self.index += 1
		if self.index > self.nop:
                       self.index = self.nop
		       return
		else:
                       self.openTest()

        def key_up(self):
		return            


	def key_down(self):
		return

	def keyNumberGlobal(self, number):
		# Calculate index
		number -= 1
		if len(self["menu"].list) > number:
			self["menu"].setIndex(number)
			self.okbuttonClick()

	def closeNonRecursive(self):
                self.close(False)

	def closeRecursive(self):
                self.close(True)

	def createSummary(self):
                return

	def keyNumberGlobal(self, number):
		##print "menu keyNumber:", number
		# Calculate index
		number -= 1
		if len(self["menu"].list) > number:
			self["menu"].setIndex(number)
			self.okbuttonClick()

	def closeNonRecursive(self):
                self.close(False)

	def closeRecursive(self):
                self.close(True)

	def createSummary(self):
#                return MenuSummary
                return

        def okbuttonClick(self):
           idx = self.index - 1
           selection = self.tlist[idx]
           print "selection =", selection
	   if selection is not None:
		  selection[1]()
		  
######################################

class IconMain(Screen):

	def __init__(self, session, tlist, menuTitle):
		Screen.__init__(self, session)
		self.skinName = "Iconmain"
                self.tlist = tlist
                ipage = 1
                list = []
		nopic = len(self.tlist)
                self.pos = []
		self.ipage = 1
		self.index = 0
		
		title = menuTitle
		self["title"] = Button(title)
		
		self.icons = []
		self.indx = []
		n1 = len(tlist)
		self.picnum = n1
		
		list = []
		tlist = []

                self["label1"] = StaticText()
                self["label2"] = StaticText()
                self["label3"] = StaticText()
                self["label4"] = StaticText()
                self["label5"] = StaticText()
                self["label6"] = StaticText()
                
                self["label1s"] = StaticText()
                self["label2s"] = StaticText()
                self["label3s"] = StaticText()
                self["label4s"] = StaticText()
                self["label5s"] = StaticText()
                self["label6s"] = StaticText()                

                self["pointer"] = Pixmap()
                self["pixmap1"] = Pixmap()
                self["pixmap2"] = Pixmap()
                self["pixmap3"] = Pixmap()
                self["pixmap4"] = Pixmap()
                self["pixmap5"] = Pixmap()
                self["pixmap6"] = Pixmap()
         
	        
		self["red"] = Button(_("Exit"))
		self["green"] = Button(_("Select"))
		self["yellow"] = Button(_("Config"))
                		
		self["actions"] = NumberActionMap(["OkCancelActions", "MenuActions", "DirectionActions", "NumberActions", "ColorActions"],
			{
				"ok": self.okbuttonClick,
				"cancel": self.closeNonRecursive,
				"left": self.key_left,
			        "right": self.key_right,
			        "up": self.key_up,
			        "down": self.key_down,
                                "red": self.cancel,
			        "green": self.okbuttonClick,
			        "yellow": self.key_menu,
				"menu": self.closeRecursive,
				"1": self.keyNumberGlobal,
				"2": self.keyNumberGlobal,
				"3": self.keyNumberGlobal,
				"4": self.keyNumberGlobal,
				"5": self.keyNumberGlobal,
				"6": self.keyNumberGlobal,
				"7": self.keyNumberGlobal,
				"8": self.keyNumberGlobal,
				"9": self.keyNumberGlobal
			})
                self.index = 0
                i = 0
                self.maxentry = 29
                self.istart = 0

                i = 0
 
                self.onShown.append(self.openTest)



        def key_menu(self):
                return
                
        def cancel(self):
                self.close()
                      
        def paintFrame(self):
                pass

        def openTest(self):
                if self.ipage == 1:
                        ii = 0
                elif self.ipage == 2:
                        ii = 6
                elif self.ipage == 3:
                        ii = 12
                elif self.ipage == 4:
                        ii = 18 
                elif self.ipage == 5:
                        ii = 24 
                        
                dxml = config.skin.primary_skin.value
                dskin = dxml.split("/")
#                if dskin[0] == "skin.xml":                                       
                j = 0
                i = ii
                while j<6:
                        j = j+1
                        if i > (self.picnum-1):
                                icon = dskin[0] + "/blank.png"
                                name = ""
                        else:                        
                                name = self.tlist[i][0]

                        if "AutoBouquetsMaker" in name:
                                name = "AutoBouquets\nMakerProvider" 
                        if len(name) > 14:
                            if ("-" in name) or ("/" in name) or (" " in name):
                                name = name.replace("-", "\n-")
                                name = name.replace(" /", "/")
                                name = name.replace("/ ", "/")
                                name = name.replace(" ", "\n")
                            else:
                                name = name[:14] + "\n-" + name[12:]    
                        if "A/V" not in name:
                                name = name.replace("/", "\n")
                 	if j == (self.index + 1):
                                self["label" + str(j)].setText(" ")
 	                        self["label" + str(j) + "s" ].setText(name)
                        else:
                                self["label" + str(j)].setText(name)
 	                        self["label" + str(j) + "s" ].setText(" ")
 	                
		        i=i+1  
                j = 0
                i = ii
                while j<6:
                         j = j+1
                         itot = (self.ipage - 1)*6 + j
                         if itot > (self.picnum):
                                icon = "/usr/share/enigma2/" + dskin[0] + "/blank.png"
                         else:                        
                                icon = "/usr/share/enigma2/" + dskin[0] + "/buttons/icon1.png"
                         pic = icon 
                         self["pixmap" + str(j)].instance.setPixmapFromFile(pic)
                         i = i+1
                if self.picnum > 6:
#                         self["pointer"].instance.setPixmapFromFile(dskin[0] + "/pointer.png")
                         try:       
                                dpointer = "/usr/share/enigma2/" + dskin[0] + "/pointer.png"
                                self["pointer"].instance.setPixmapFromFile(dpointer)
                         except:  
                                dpointer = "/usr/share/enigma2/skin_default/pointer.png"
                                self["pointer"].instance.setPixmapFromFile(dpointer)

                else:
                         try:       
                                dpointer = "/usr/share/enigma2/" + dskin[0] + "/blank.png"
                                self["pointer"].instance.setPixmapFromFile(dpointer)
                         except:  
                                dpointer = "/usr/share/enigma2/skin_default/blank.png"
                                self["pointer"].instance.setPixmapFromFile(dpointer)
                
        def key_left(self):
                self.index -= 1
                inum = self.picnum - 1 -(self.ipage - 1)*6
                if (self.index < 0):
                        if inum < 5:
		               self.index = inum
		        else: 
                               self.index = 5
		self.openTest()

        def key_right(self):
		self.index += 1
		inum = self.picnum - 1 -(self.ipage - 1)*6
                if (self.index > inum) or (self.index > 5):
                        self.index = 0
                self.openTest()

        def key_up(self):
		self.ipage = self.ipage -1
		if (self.ipage <1) and (7>self.picnum > 0):
		       self.ipage = 1 
		elif (self.ipage <1) and (13>self.picnum > 6):
		       self.ipage = 2
		elif (self.ipage <1) and (19>self.picnum > 12):
		       self.ipage = 3 
                elif (self.ipage <1) and (25>self.picnum > 18):
		       self.ipage = 4 
                elif (self.ipage <1) and (31>self.picnum > 24):
		       self.ipage = 5 
		self.index = 0
                self.openTest()               


	def key_down(self):
		self.ipage = self.ipage +1
		if (self.ipage ==2) and (7>self.picnum > 0):
		       self.ipage = 1 
		elif (self.ipage ==3) and (13>self.picnum > 6):
		       self.ipage = 1
		elif (self.ipage ==4) and (19>self.picnum > 12):
		       self.ipage = 1 
                elif (self.ipage ==5) and (25>self.picnum > 18):
		       self.ipage = 1 
		elif (self.ipage ==6) and (31>self.picnum > 24):
		       self.ipage = 1 
                self.index = 0              
		self.openTest()  

	def keyNumberGlobal(self, number):
		# Calculate index
		number -= 1
		if len(self["menu"].list) > number:
			self["menu"].setIndex(number)
			self.okbuttonClick()

	def closeNonRecursive(self):
                self.close(False)

	def closeRecursive(self):
                self.close(True)

	def createSummary(self):
                return

	def keyNumberGlobal(self, number):
		##print "menu keyNumber:", number
		# Calculate index
		number -= 1
		if len(self["menu"].list) > number:
			self["menu"].setIndex(number)
			self.okbuttonClick()

	def closeNonRecursive(self):
                self.close(False)

	def closeRecursive(self):
                self.close(True)

	def createSummary(self):
#                return MenuSummary
                return

        def okbuttonClick(self):
           if self.ipage == 1:
                   idx = self.index
           elif self.ipage == 2:
                   idx = self.index + 6
           elif self.ipage == 3:
                   idx = self.index + 12
           elif self.ipage == 4:
                   idx = self.index + 18   
           elif self.ipage == 5:
                   idx = self.index + 24               
           if idx > (self.picnum-1):
                   return

           if idx is None:
                return
#           self.name = self.icons[idx][:-4]

           selection = self.tlist[idx]
           print "selection =", selection
	   if selection is not None:
		  selection[1]()
##################### pcd end ###############
		

class MainMenu(Menu):
	#add file load functions for the xml-file

	def __init__(self, *x):
		self.skinName = "Menu"
		Menu.__init__(self, *x)
