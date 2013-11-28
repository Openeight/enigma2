import urllib
from urllib2 import urlopen
from Components.MenuList import MenuList
from Components.Label import Label

from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import NumberActionMap
from Components.Input import Input
from Components.Pixmap import Pixmap
from Components.FileList import FileList
from Screens.ChoiceBox import ChoiceBox
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Screens.InputBox import InputBox

#from twisted.web.client import getPage, downloadPage
import os

import gettext

def _(txt):
	t = gettext.dgettext("XTPanel", txt)
	if t == txt:
		print "[XTPanel] fallback to default translation for", txt
		t = gettext.gettext(txt)
	return t

###############################
# Coded by PCD, july 2009     #
###############################

class Ipkinstall(Screen):

    skin = """
		<screen position="center,center" size="550,400" title=" " >
			<!--widget name="text" position="0,0" size="550,25" font="Regular;20" /-->
			<widget name="list" position="10,0" size="500,350" scrollbarMode="showOnDemand" />
			<!--widget name="pixmap" position="200,0" size="190,250" /-->
			<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />
			<widget name="info" position="100,230" zPosition="4" size="300,25" font="Regular;18" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />
		</screen>"""

    def __init__(self, session):
		self.skin = Ipkinstall.skin
		Screen.__init__(self, session)

        	self["list"] = MenuList([])
		self["info"] = Label()
                self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
                self.icount = 0
                title = _("Available for install")
                self.setTitle(title)
                self.onLayoutFinish.append(self.openTest)

    def openTest(self):
                self.ipks = []
 		path = "/tmp/"
		for root, dirs, files in os.walk(path):
			for name in files:
			        if name[-4:] == ".ipk":
				      self.icount = self.icount +1
                                      fname = "/tmp/" + name
                                      self.ipks.append(fname)
                path2 = "/media/usb/"
		for root, dirs, files in os.walk(path2):
			for name in files:
			        if name[-4:] == ".ipk":
				      self.icount = self.icount +1
                                      fname = "/tmp/" + name
                                      self.ipks.append(fname)                     
 
                self["list"].setList(self.ipks)


    def okClicked(self):
	   if self.icount>0:
                sel = self["list"].getSelectionIndex()
                ipk = self.ipks[sel]
                self.session.open(Getipk, ipk)
                self.close()
               
    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()
	
    def keyNumberGlobal(self, number):
		print "pressed", number
		self["text"].number(number)		
		

class Getipk(Screen):

    skin = """
		<screen position="80,70" size="600,470" title="Install status" >
			<!--widget name="text" position="0,0" size="550,25" font="Regular;20" /-->
			<widget name="list" position="10,0" size="590,400" scrollbarMode="showOnDemand" />
			<!--widget name="pixmap" position="200,0" size="190,250" /-->
			<eLabel position="70,100" zPosition="-1" size="100,69" backgroundColor="#222222" />
			<widget name="info" position="100,420" zPosition="4" size="300,25" font="Regular;18" foregroundColor="#ffffff" transparent="1" halign="center" valign="center" />
		</screen>"""

    def __init__(self, session, ipk):
		self.skin = Getipk.skin
		Screen.__init__(self, session)

        	self["list"] = MenuList([])
		self["info"] = Label()
                self["actions"] = ActionMap(["OkCancelActions"], {"ok": self.okClicked, "cancel": self.close}, -1)
                self.icount = 0
                self.ipk = ipk
                self["info"].setText("Installing ipkg......") 
                title = _("Install status")
                self.setTitle(title)
                self.onLayoutFinish.append(self.openTest)
   
    
    def openTest(self):
                print "OK!!!!"
#                self.session.open(Ipkinstall)
                cmd = "opkg install --force-overwrite --force-depends " + self.ipk + ">/tmp/ipk.log"
                os.system(cmd)
#                self.session.open(Viewlog)
                self.viewLog()

  
    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()
		

    def keyNumberGlobal(self, number):
		print "pressed", number
		self["text"].number(number)		

    def viewLog(self):
          self["info"].setText("Press OK to continue...")
          if os.path.isfile("/tmp/ipk.log")is not True :
                cmd = "touch /tmp/ipk.log"
                os.system(cmd)
	  else:     	
                myfile = file(r"/tmp/ipk.log")
                icount = 0
                data = []
                ebuf = []
                for line in myfile.readlines():
                      data.append(icount)
                      print line
                      num = len(line)
                      if num < 55 :
                            data[icount] = (line[:-1])
                            print data[icount]
#                            if icount>0:
                            ebuf.append(data[icount])
                                  
                      else :
                            print line
                            dataFull = line
                            print dataFull
                            data1 = dataFull[:55]
                            print data1
                            data[icount] = data1
                            print data[icount]
#                            if icount>0:
                            ebuf.append(data[icount])
                              
                            data2 = '               ' + dataFull[55:]
                            print data2
                            data[icount] = data2
                            print data[icount]
#                            if icount>0:
                            ebuf.append(data[icount])
                                      
                      icount = icount + 1
                      self["list"].setList(data)
                      self.endinstall()

    def endinstall(self):
                ipkname = self.ipk  
                if ipkname != 0:               
                       print "ipk name =", ipkname 
#                       ipos = ipkname.find("_")
#                       remname = ipkname[:ipos]
#                       print "remname =", remname
                       f=open('/etc/ipklist_installed', 'a')
                       f1= ipkname + "\n"
                       f.write(f1)
                       cmd = "rm /tmp/"  + ipkname
                       os.system(cmd)                 
 
    def okClicked(self):
            self.close() 
               















