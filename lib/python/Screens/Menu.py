######################################################
# This python script includes amendment by           #
# pcd@i-have-a-dreambox June 2013 to the original    #
# Menu.py under the original Licence. You may freely #
# modify and distribute this amendment provided you  #
# keep this Licence.                                 #
######################################################
from Screen import Screen
from Components.Sources.List import List
from Components.ActionMap import NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.config import configfile
from Components.PluginComponent import plugins
from Components.config import config
from Components.SystemInfo import SystemInfo

from Tools.Directories import resolveFilename, SCOPE_SKIN

import xml.etree.cElementTree

from Screens.Setup import Setup, getSetupTitle

from Components.Pixmap import Pixmap, MovingPixmap
from Components.Sources.StaticText import StaticText
import os
from Components.Button import Button

# read the menu
mdom = xml.etree.cElementTree.parse(resolveFilename(SCOPE_SKIN, 'menu.xml'))

class boundFunction:
	def __init__(self, fnc, *args):
		self.fnc = fnc
		self.args = args
	def __call__(self):
		self.fnc(*self.args)
		
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
	skin = """
	<screen position="0,0" size="132,64">
		<widget source="parent.title" render="Label" position="6,4" size="120,21" font="Regular;18" />
		<!--widget source="parent.menu" render="Label" position="6,25" size="120,21" font="Regular;16">
			<convert type="StringListSelection" />
		</widget-->
		<widget source="global.CurrentTime" render="Label" position="56,46" size="82,18" font="Regular;16" >
			<convert type="ClockToText">WithSeconds</convert>
		</widget>
	</screen>"""

class Menu(Screen):
	ALLOW_SUSPEND = True


	def okbuttonClick(self):
		if self.menuID is not None:
                        pass
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
				list.append((l[0], boundFunction(l[1], self.session), l[2], l[3] or 50))

		# for the skin: first try a menu_<menuID>, then Menu
		self.skinName = [ ]
		self.menuID = menuID
		skfile = "/usr/share/enigma2/" + config.skin.primary_skin.value 
                f1 = file(skfile, "r")
                self.sktxt = f1.read()
                f1.close()    
                if menuID is not None:	
		    if (config.usage.mainmenu_mode.value == "horz") and ('<screen name="Iconmain" ' in self.sktxt):	
                        self.skinName.append("Iconmain")
                    else:    
                        self.skinName.append("menu_" + menuID)
                else:
                        self.skinName.append("Menu")

                title = self.menuID
                self.setTitle(title)


		# Sort by Weight
		list.sort(key=lambda x: int(x[3]))

		self.tlist = list
                self["menu"] = List(list)
                
               
                dxml = config.skin.primary_skin.value
                dskin = dxml.split("/")
                if dskin[0] == "skin.xml":
                        menupath = "skin_default/menu/"
                else:        
                        menupath = dskin[0] + "/buttons/"       
                self.pics = []
                ip = 0
                for x in list:
                                                       
                        pic = x[2] + ".png"        
                        pixpath = menupath + pic
                        pix = resolveFilename(SCOPE_SKIN, pixpath)
                        self.pics.append(pix)
                                               
		self["actions"] = NumberActionMap(["OkCancelActions", "MenuActions", "DirectionActions", "NumberActions"],
			{
				"ok": self.okbuttonClick,
				"cancel": self.closeNonRecursive,
				"left": self.key_left,
			        "right": self.key_right,
			        "up": self.key_up,
			        "down": self.key_down,

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
		
		self.setTitle(a)
		
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
                
                if (config.usage.mainmenu_mode.value == "horz") and ('<screen name="Iconmain" ' in self.sktxt):
                        self.onShown.append(self.openTest)
                self.index = 0
                self.maxentry = len(list)-1

        def openTest(self):
                 self.session.open(IconMain, self.pics, self.tlist, self.menu_title) 
                 self.close()


        def key_left(self):
		self.index -= 1
		if self.index < 0:
			self.index = self.maxentry
		self.paintFrame()

	def key_right(self):
		self.index += 1
		if self.index > self.maxentry:
			self.index = 0
		self.paintFrame()

	def key_up(self):
		self.index = self.index - 4
		if self.index < 0:
			self.index = self.maxentry
		self.paintFrame()

	def key_down(self):
                self.index = self.index + 4
		if self.index > self.maxentry:
			self.index = 0
		self.paintFrame()


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
#                return MenuSummary
                return
        def submenu(self, parent):
		self["menu"] = List(list)
		self.skinName = self.skinName2

######################################

class IconMain(Screen):

	def __init__(self, session, pix, tlist, menuTitle):
		Screen.__init__(self, session)
		self.skinName = "Iconmain"
                self.tlist = tlist
                ipage = 1
                list = []
		
		self.pics = []
		nopic = len(pix)
		
                i = 0
		while i< nopic:
                      self.pics.append((pix[i], i)) 
		      i = i+1

                pics = self.pics
                self.pos = []
		self.ipage = 1
		self.index = 0
		
		title = menuTitle
		self["title"] = Button(title)
		
		self.icons = []
		self.indx = []
		n1 = len(pics)
		self.picnum = n1
		i = 0
		while i<n1:
		     self.icons.append(i)
		     self.icons[i] = pics[i][0]
		     self.indx.append(i)
                     self.indx[i] = pics[i][1]
                     i = i+1 
		
		list = []
		tlist = []
		self.pics = pics

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
				"cancel": self.cancel,
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
           self.name = self.icons[idx][:-4]

           selection = self.tlist[idx]
	   if selection is not None:
		  selection[1]()
####################################



class MainMenu(Menu):
	#add file load functions for the xml-file
	
	def __init__(self, *x):
#		self.skinName = "Menu"
#                self.skinName = "Iconmain"
		Menu.__init__(self, *x)






