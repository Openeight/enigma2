
from Components.MenuList import MenuList
from Components.Label import Label

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Pixmap import Pixmap
from Components.FileList import FileList
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap

class ExtraSetup(Screen):
    def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = "Settings"
                title = "Install Skin Settings"
                self.setTitle(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
                self["actions"] = ActionMap(["OkCancelActions"], {"cancel": self.close}, -1)
                txt = _("")
                self["info"].setText(txt)
                self.onShown.append(self.startSession)

    def startSession(self):
                try:
                        from Plugins.Extensions.ExtrasPanel.plugin import Extraspanel
                        self.session.open(Extraspanel)
                        self.close()
                except:        
                        self.session.open(MessageBox, _("Plugin ExtrasPanel is not installed !"), MessageBox.TYPE_ERROR, timeout = 10)
                        self.close()






