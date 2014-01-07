
from Components.MenuList import MenuList
from Components.Label import Label

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Pixmap import Pixmap
from Components.FileList import FileList
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap
from Components.config import config
from Screens.Standby import TryQuitMainloop

class SkinSetup(Screen):
    def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = "Settings"
                title = "Setup Skin"
                self.setTitle(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
#		self["KEY_HELP"] = Button(_("HELP"))
#                self["actions"] = ActionMap(["OkCancelActions", "HelpActions"], {"ok": self.okClicked, "cancel": self.close, "displayHelp" : self.readme}, -1)
                self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
                txt = _("Here you can change skin, configure mainmenu or configure second-infobar, or configure skin XTA.")
                self["info"].setText(txt)
                self.onShown.append(self.startSession)

    def startSession(self):
                self.res = []
                self.res.append(_("Install Skin"))
                self.res.append(_("Configure mainmenu"))
                self.res.append(_("Configure second-infobar"))
		self.res.append(_("Show Picons in Channel List"))
                self.res.append(_("XTAskin Setup"))
                self.res.append(_("Exit"))
                self["list"].setList(self.res)
    
    def okClicked(self):
                ires = self["list"].getSelectionIndex()
		if ires == 0:
		        self.startskin()
		elif ires == 1:
		        self.session.open(SettingsB)  
                elif ires == 2:
		        self.session.open(SettingsC) 
		elif ires == 3:
		        self.session.open(SettingsD)
                elif ires == 4:
		        self.xtaskin()  
               				
		else:
                        self.close()
                        
    def startskin(self):                         
                try:        
                        from Plugins.SystemPlugins.SkinSelector.plugin import SkinSelector
                        self.session.open(SkinSelector) 
                except:        
                        self.session.open(MessageBox, _("SystemPlugins SkinSelector is not installed !"), MessageBox.TYPE_ERROR, timeout = 10)
                        self.close()

    def xtaskin(self):                         
                try:        
                        from Plugins.Extensions.iSkin.plugin import MenuStart
                        self.session.open(MenuStart) 
                except:        
                        self.session.open(MessageBox, _("Plugin iSkin is not installed !"), MessageBox.TYPE_ERROR, timeout = 10)
                        self.close()



class SettingsB(Screen):
    def __init__(self, session):
		Screen.__init__(self, session)
                self.skinName = "Settings"
                title = "Configure Mainmenu"
                self.setTitle(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
#		self["KEY_HELP"] = Button(_("HELP"))
#                self["actions"] = ActionMap(["OkCancelActions", "HelpActions"], {"ok": self.okClicked, "cancel": self.close, "displayHelp" : self.readme}, -1)
                self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
                self.cur = config.usage.mainmenu_mode.value
                if self.cur == "horz":
                        txt = "Current Mainmenu list setting is Horizontal.\nHere you can change it.\nAfter select enigma will restart."
                elif self.cur == "vert":
                        txt = "Current Mainmenu list setting is Vertical.\nHere you can change it.\nAfter select enigma will restart."
                self["info"].setText(txt)
                self.onLayoutFinish.append(self.startSession)

    def startSession(self):
                self.res = []
                self.res.append("Horizontal list")
                self.res.append("Vertical list")
                self.res.append("Exit")
                self["list"].setList(self.res)
    
    def okClicked(self):
                ires = self["list"].getSelectionIndex()
		if ires == 0:
		        self.Horz()
		elif ires == 1:
		        self.Vert()        
		else:
                        self.close()
                        
    def Horz(self):
          if self.cur == "horz":
                self.session.open(MessageBox, _("Current mainmenu setting is Horizontal !"), type = MessageBox.TYPE_INFO,timeout = 10 )
          else:
                config.usage.mainmenu_mode.value = "horz"
    	        config.usage.mainmenu_mode.save()
    	        self.session.open(TryQuitMainloop, 3) 

    def Vert(self):
          if self.cur == "vert":
                self.session.open(MessageBox, _("Current mainmenu setting is Vertical !"), type = MessageBox.TYPE_INFO,timeout = 10 )
          else:
                config.usage.mainmenu_mode.value = "vert"
    	        config.usage.mainmenu_mode.save()
    	        self.session.open(TryQuitMainloop, 3) 
    
class SettingsC(Screen):
    def __init__(self, session):
		Screen.__init__(self, session)
                self.skinName = "Settings"
                title = "Configure second-infobar"
                self.setTitle(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
#		self["KEY_HELP"] = Button(_("HELP"))
#                self["actions"] = ActionMap(["OkCancelActions", "HelpActions"], {"ok": self.okClicked, "cancel": self.close, "displayHelp" : self.readme}, -1)
                self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
                self.cur = config.usage.show_second_infobar.value
                txt = " " 
                if self.cur is None:
                        txt = "Current Second-infobar setting is None.\nHere you can change it."
                else:
                        txt = "Current Second-infobar setting is Show.\nHere you can change it."
                self["info"].setText(txt)
                self.onLayoutFinish.append(self.startSession)

    def startSession(self):
                self.res = []
                self.res.append("Show second-infobar")
                self.res.append("Remove second-infobar")
                self.res.append("Exit")
                self["list"].setList(self.res)
    
    def okClicked(self):
                ires = self["list"].getSelectionIndex()
		if ires == 0:
		        self.ShowSI()
		elif ires == 1:
		        self.RemSI()        
		else:
                        self.close()
                        
    def ShowSI(self):
          if self.cur is not None:
                self.session.open(MessageBox, _("Current Second-infobar setting is Show !"), type = MessageBox.TYPE_INFO,timeout = 10 )
          else:
                config.usage.show_second_infobar.value = int(0)
    	        config.usage.show_second_infobar.save()

#    	        self.session.open(TryQuitMainloop, 3)

    def RemSI(self):
          if self.cur is None:
                self.session.open(MessageBox, _("Current Second-infobar setting is None !"), type = MessageBox.TYPE_INFO,timeout = 10 )
          else:
                config.usage.show_second_infobar.value = None
    	        config.usage.show_second_infobar.save()
#    	        self.session.open(TryQuitMainloop, 3)

class SettingsD(Screen):
    def __init__(self, session):
		Screen.__init__(self, session)
                self.skinName = "Settings"
                title = "Show Picons in Channel List"
                self.setTitle(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
#		self["KEY_HELP"] = Button(_("HELP"))
#                self["actions"] = ActionMap(["OkCancelActions", "HelpActions"], {"ok": self.okClicked, "cancel": self.close, "displayHelp" : self.readme}, -1)
                self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
                self.cur = config.usage.service_icon_enable.value
                txt = " " 
                if self.cur is True:
                        txt = "Current picon setting is True.\nHere you can change it."
                else:
                        txt = "Current picon setting is False.\nHere you can change it."
                self["info"].setText(txt)
                self.onLayoutFinish.append(self.startSession)

    def startSession(self):
                self.res = []
                self.res.append("Show Picons in Channel List")
                self.res.append("Remove Picons in Channel List")
                self.res.append("Exit")
                self["list"].setList(self.res)
    
    def okClicked(self):
                ires = self["list"].getSelectionIndex()
		if ires == 0:
		        self.ShowSp()
		elif ires == 1:
		        self.RemSp()        
		else:
                        self.close()
                        
    def ShowSp(self):
          if self.cur is True:
                self.session.open(MessageBox, _("Current picon setting is True !"), type = MessageBox.TYPE_INFO,timeout = 10 )
          else:
                config.usage.service_icon_enable.value = True
    	        config.usage.service_icon_enable.save()

#    	        self.session.open(TryQuitMainloop, 3)

    def RemSp(self):
          if self.cur is False:
                self.session.open(MessageBox, _("Current picon setting is False !"), type = MessageBox.TYPE_INFO,timeout = 10 )
          else:
                config.usage.service_icon_enable.value = False
    	        config.usage.service_icon_enable.save()
#    	        self.session.open(TryQuitMainloop, 3)
    






































