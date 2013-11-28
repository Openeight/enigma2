from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Input import Input
from Components.Pixmap import Pixmap
from Components.FileList import FileList
from Screens.ChoiceBox import ChoiceBox
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console

import os

import gettext

def _(txt):
	t = gettext.dgettext("XTPanel", txt)
	if t == txt:
		print "[XTPanel] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t
###############################
# Coded by PCD, February 2008 #
###############################

class Ipkremove(Screen):
	skin = """
		<screen position="100,100" size="550,400" title="Ipkremove" >
			<widget name="list" position="10,0" size="190,250" scrollbarMode="showOnDemand" />
			<widget name="pixmap" position="200,0" size="190,250" />
		</screen>"""
	def __init__(self, session, args = None):
		self.skin = Ipkremove.skin
		Screen.__init__(self, session)

		self["list"] = FileList("/", matchingPattern = "^.*\.(ipk|png|avi|mp3|mpeg|ts)")
		self["pixmap"] = Pixmap()
		
		self["text"] = Input("1234", maxSize=True, type=Input.NUMBER)
				
		self["actions"] = NumberActionMap(["WizardActions", "InputActions"],
		{
			"ok": self.close,
			"back": self.close,
			"left": self.keyLeft,
			"right": self.keyRight,
		}, -1)
		title = _("Ipkremove")
                self.setTitle(title)
		self.onShown.append(self.openTest)

	def openTest(self):
                fpath = "/etc/ipkinst"
                tlist = []
                for root, dirs, files in os.walk(fpath):
                     for name in files:
                        n1 = name.find("_", 0)
                        name2 = name[:n1]
		        tlist.append([name, name2])
                ipkres = self.session.openWithCallback(self.test2, ChoiceBox, title=(_("Please select ipkg to remove")), list=tlist)
                
        def test2(self, returnValue):
                if returnValue is None:
                       self.close()
                else: 
                       print "returnValue", returnValue
                       remname = returnValue[1]
                       ipk = returnValue[0]
 	               print "ipkname =", ipk
                       cmd1 = "opkg remove " + remname
                       cmd2 = "rm /etc/ipkinst/" + ipk
                       cmd = cmd1 + " && " + cmd2
                       print cmd
                       title = _("Removing addon %s" %(remname))
                       self.session.open(Console,_(title),[cmd])
                self.close()
                       	
	def keyLeft(self):
		self["text"].left()
	
	def keyRight(self):
		self["text"].right()
		
              	
	
	def ok(self):
		self.close()
	
	def keyNumberGlobal(self, number):
		print "pressed", number
		self["text"].number(number)















