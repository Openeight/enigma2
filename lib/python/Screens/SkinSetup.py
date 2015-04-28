
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
from Screens.Downloads import Getipklist
from Screens.Ipkremove import Ipkremove

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
                txt = _("Here you can change skin, configure mainmenu, configure second-infobar or configure TechniHD skin.")
                self["info"].setText(txt)
                self.onShown.append(self.startSession)

    def startSession(self):
                self.res = []
                self.res.append(_("Skin Manager"))
                self.res.append(_("Configure mainmenu"))
                self.res.append(_("Configure second-infobar"))
		self.res.append(_("Show Picons in Channel List"))
                self.res.append(_("TechniHD Setup"))
                self.res.append(_("Exit"))
                self["list"].setList(self.res)
    
    def okClicked(self):
                ires = self["list"].getSelectionIndex()
		if ires == 0:
		        self.session.open(SettingsA)  
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
                        

    def xtaskin(self):                         
                try:        
                        from Plugins.Extensions.TechniHDSetup.plugin import TechniHDSetup
                        self.session.open(TechniHDSetup) 
                except:        
                        self.session.open(MessageBox, _("TechniHD is not installed on your Xtrend box !"), MessageBox.TYPE_ERROR, timeout = 10)
                        self.close()

class SettingsA(Screen):
    def __init__(self, session):
		Screen.__init__(self, session)
                self.skinName = "Settings"
                title = _("Skin Manager")
                self.setTitle(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
#		self["KEY_HELP"] = Button(_("HELP"))
#                self["actions"] = ActionMap(["OkCancelActions", "HelpActions"], {"ok": self.okClicked, "cancel": self.close, "displayHelp" : self.readme}, -1)
                self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
                self.cur = config.usage.service_icon_enable.value
                txt = _("Here you can download, install or remove skins")
                self["info"].setText(txt)
                self.onLayoutFinish.append(self.startSession)

    def startSession(self):
                self.res = []
                self.res.append(_("Download skin"))
                self.res.append(_("Install skin"))
                self.res.append(_("Remove skin"))
                self.res.append(_("Exit"))
                self["list"].setList(self.res)
    
    def okClicked(self):
                ires = self["list"].getSelectionIndex()
		if ires == 0:
		        self.session.open(Getipklist)
		elif ires == 1:
		        self.startskin()
		elif ires == 2:
                        self.session.open(Ipkremove)
		else:
                        self.close()
                        
    def startskin(self):
                try:
                        from Plugins.SystemPlugins.SkinSelector.plugin import SkinSelector
                        self.session.open(SkinSelector)
                except:
                        self.session.open(MessageBox, _("SystemPlugins SkinSelector is not installed !"), MessageBox.TYPE_ERROR, timeout = 10)
                        self.close()


class SettingsB(Screen):
    def __init__(self, session):
		Screen.__init__(self, session)
                self.skinName = "Settings"
                title = _("Configure Mainmenu")
                self.setTitle(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
#		self["KEY_HELP"] = Button(_("HELP"))
#                self["actions"] = ActionMap(["OkCancelActions", "HelpActions"], {"ok": self.okClicked, "cancel": self.close, "displayHelp" : self.readme}, -1)
                self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
                self.cur = config.usage.mainmenu_mode.value
                if self.cur == "horzicon":
                        txt = _("Current Mainmenu list setting is Horizontal-icon.\nHere you can change it.\nAfter select enigma will restart.")
                elif self.cur == "vert":
                        txt = _("Current Mainmenu list setting is Vertical.\nHere you can change it.\nAfter select enigma will restart.")
                elif self.cur == "horzanim":
                        txt = _("Current Mainmenu list setting is Horizontal-Animated.\nHere you can change it.\nAfter select enigma will restart.")
                self["info"].setText(txt)
                self.onLayoutFinish.append(self.startSession)

    def startSession(self):
                self.res = []
                self.res.append(_("Horizontal icon list"))
                self.res.append(_("Vertical list"))
                self.res.append(_("Horizontal animated list"))
                self.res.append(_("Exit"))
                self["list"].setList(self.res)
    
    def okClicked(self):
                ires = self["list"].getSelectionIndex()
		if ires == 0:
		        self.Icon()
		elif ires == 1:
		        self.Vert()
                elif ires == 2:
		        self.Anim()         
		else:
                        self.close()
                        
    def Icon(self):
                config.usage.mainmenu_mode.value = "horzicon"
    	        config.usage.mainmenu_mode.save()
    	        self.session.open(TryQuitMainloop, 3) 

    def Vert(self):
                config.usage.mainmenu_mode.value = "vert"
    	        config.usage.mainmenu_mode.save()
    	        self.session.open(TryQuitMainloop, 3)

    def Anim(self):
                config.usage.mainmenu_mode.value = "horzanim"
    	        config.usage.mainmenu_mode.save()
    	        self.session.open(TryQuitMainloop, 3) 
    
class SettingsC(Screen):
    def __init__(self, session):
		Screen.__init__(self, session)
                self.skinName = "Settings"
                title = _("Configure second-infobar")
                self.setTitle(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
#		self["KEY_HELP"] = Button(_("HELP"))
#                self["actions"] = ActionMap(["OkCancelActions", "HelpActions"], {"ok": self.okClicked, "cancel": self.close, "displayHelp" : self.readme}, -1)
                self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
                self.cur = config.usage.show_second_infobar.value
                txt = " " 
                if self.cur is None:
                        txt = _("Current Second-infobar setting is None.\nHere you can change it.")
                else:
                        txt = _("Current Second-infobar setting is Show.\nHere you can change it.")
                self["info"].setText(txt)
                self.onLayoutFinish.append(self.startSession)

    def startSession(self):
                self.res = []
                self.res.append(_("Show second-infobar"))
                self.res.append(_("Remove second-infobar"))
                self.res.append(_("Exit"))
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
                title = _("Show Picons in Channel List")
                self.setTitle(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
#		self["KEY_HELP"] = Button(_("HELP"))
#                self["actions"] = ActionMap(["OkCancelActions", "HelpActions"], {"ok": self.okClicked, "cancel": self.close, "displayHelp" : self.readme}, -1)
                self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
                self.cur = config.usage.service_icon_enable.value
                txt = " " 
                if self.cur is True:
                        txt = _("Current picon setting is True.\nHere you can change it.")
                else:
                        txt = _("Current picon setting is False.\nHere you can change it.")
                self["info"].setText(txt)
                self.onLayoutFinish.append(self.startSession)

    def startSession(self):
                self.res = []
                self.res.append(_("Show Picons in Channel List"))
                self.res.append(_("Remove Picons in Channel List"))
                self.res.append(_("Exit"))
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
    
