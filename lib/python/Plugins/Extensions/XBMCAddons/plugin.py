# coding: utf-8
"""
    This file is part of Plugin XBMCAddons by pcd@et-view-support.com
    Copyright (C) 2013

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
from Utils import *
from Components.config import config, ConfigSubsection, ConfigText, ConfigYesNo
from Components.ConfigList import ConfigListScreen

from os import path, system

from Components.Task import Task, Job, job_manager as JobManager, Condition
from Screens.TaskView import JobView
from Screens.Console import Console
from Components.Button import Button
from Tools.Directories import fileExists, copyfile
from Tools.LoadPixmap import LoadPixmap
######################
import xml.etree.cElementTree 
import gettext
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Sources.List import List
from enigma import eTimer
from SkinLoader import loadPluginSkin
##########################
import xbmcaddon
import re
import datetime,time
##########################
try:
       import Image
except:
       pass       

THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons"
ARG = " "
DEBUG = 0
######################

def Log(text):
              file = open("/tmp/xbmclog.txt", "a")
              text = text + "\n"
              file.write(text)
              file.close()

def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters.split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict

def getpics(names, pics, tmpfold, picfold):
              cmd = "rm " + tmpfold + "/*"
              os.system(cmd)
              npic = len(pics)
              pix = []
              j = 0
              while j < npic:
                   name = names[j]
                   name = name.replace("&", "")
                   name = name.replace(":", "")
                   url = pics[j]
                   if url is None:
                          url = " "
                   if ".png" in url:
                          tpicf = tmpfold + "/" + name + ".png"
                          picf = picfold + "/" + name + ".png"
                   else:       
                          tpicf = tmpfold + "/" + name + ".jpg"
                          picf = picfold + "/" + name + ".jpg"
                          
                   if fileExists(picf):
                          cmd = "cp " + picf + " " + tmpfold
                          os.system(cmd)
                   
                   if not fileExists(picf):
                       if THISPLUG in url:
                          try:
                                  cmd = "cp " + url + " " + tpicf
                                  os.system(cmd)
                          except:
                                  pass
                       else:
                          try:
                                  cmd = "wget -O '" + tpicf +"' -c '" + url + "'"
                                  os.system(cmd)
                                  
                          except:
                                  if ".png" in tpicf:
                                          cmd = "cp " + THISPLUG + "/images/default.png " + tpicf
                                  else:
                                          cmd = "cp " + THISPLUG + "/images/default.jpg " + tpicf
                                  os.system(cmd)
                                  
                       if not fileExists(tpicf): 
                                  if ".png" in tpicf:
                                          cmd = "cp " + THISPLUG + "/images/default.png " + tpicf
                                  else:
                                          cmd = "cp " + THISPLUG + "/images/default.jpg " + tpicf
                                  os.system(cmd)

                   try:
                          im = Image.open(tpicf)
                          imode = im.mode
                          if im.mode != "P":
                                 im = im.convert("P")
                          w = im.size[0]
                          d = im.size[1]
                          r = float(d)/float(w)
                          d1 = r*200
                          if w != 200:        
                                 x = int(200)
                                 y = int(d1)
                                 im = im.resize((x,y), Image.ANTIALIAS)
                          tpicf = tmpfold + "/" + name + ".png"
                          picf = picfold + "/" + name + ".png"
                          im.save(tpicf)

                   except:
                          pass  
                   pix.append(j)
                   pix[j] = picf
                   j = j+1       
              cmd1 = "cp " + tmpfold + "/* " + picfold + " && rm " + tmpfold + "/* &"
              os.system(cmd1)
              return pix
                  
def asxurl(url):
              cmd = "wget -O /tmp/vid.asx " + url + " && sleep 2"
              system(cmd)
                           
              if not path.exists("/tmp/vid.asx"):
                      return url
              else:
                       myfile = file(r"/tmp/vid.asx")       
                       fpage = myfile.read()
                       myfile.close()
    
                       n1 = fpage.find("href", 0)
                       if n1<0:
                               return
                       n2 = fpage.find('"', (n1+10))
                       if n2<0:
                               return         
                       url1 = fpage[(n1+6):n2]
    
              return url1
              
def up(names, tmppics, pos, menu, pixmap):
                menu.up()
                pos = pos - 1
                num = len(names)
                if pos == -1:
                              pos = num - 1
                              menu.moveToIndex(pos)  
                name = names[pos]
                if name == "Exit":
                         pic1 = THISPLUG + "/images/Exit.png"
                         pixmap.instance.setPixmapFromFile(pic1)
                else:
                         pic1 = tmppics[pos]
                         pixmap.instance.setPixmapFromFile(pic1)
                return pos
                
def down(names, tmppics, pos, menu, pixmap):
                menu.down()
                pos = pos + 1
                num = len(names)
                if pos == num:
                              pos = 0
                              menu.moveToIndex(pos) 
                name = names[pos]
                if name == "Exit":
                         pic1 = THISPLUG + "/images/Exit.png"
                         pixmap.instance.setPixmapFromFile(pic1)
                else:
                         pic1 = tmppics[pos]
                         pixmap.instance.setPixmapFromFile(pic1)
                return pos
                      
def left(names, tmppics, pos, menu, pixmap):
         menu.pageUp()
         pos = menu.getSelectionIndex()
         name = names[pos]
         
         if name != "Exit":
                pic1 = tmppics[pos]
                pixmap.instance.setPixmapFromFile(pic1)

         else:      
                pic1 = THISPLUG + "/images/Exit.png"
                pixmap.instance.setPixmapFromFile(pic1)        
         return pos
         
def right(names, tmppics, pos, menu, pixmap):
         menu.pageDown()
         pos = menu.getSelectionIndex()
         name = names[pos]
         if name != "Exit":
                pic1 = tmppics[pos]
                pixmap.instance.setPixmapFromFile(pic1)
         else:      
                pic1 = THISPLUG + "/images/Exit.png"
                pixmap.instance.setPixmapFromFile(pic1)                       
         return pos                  
                
config.plugins.xbmcplug = ConfigSubsection()
config.plugins.xbmcplug.tempdel = ConfigYesNo(True)
config.plugins.xbmcplug.cachefold = ConfigText("/media/hdd", False)
config.plugins.xbmcplug.debug = ConfigYesNo(False)

class XbmcConfigScreen(ConfigListScreen,Screen):
   	skin = """
                <screen name="XbmcConfigScreen" position="center,center" size="1280,720" title="Plugin Configuration" >
                        <ePixmap position="0,0" zPosition="-2" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/images/panel3.png" />
                        <ePixmap position="942,372" size="200,200" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/images/default.png" alphatest="on" />

                        <ePixmap name="red"    position="100,400"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />
	                <ePixmap name="green"  position="240,400" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />

	                <widget name="key_red" position="100,400" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> 
	                <widget name="key_green" position="240,400" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> 

	                <widget name="config" position="100,130" size="550,140" backgroundColor="#000000" scrollbarMode="showOnDemand" />
                        <ePixmap position="100,650" zPosition="1" size="50,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/images/Exit2.png" />
         
               </screen>"""   	
	
   	
	def __init__(self, session, args = 0):
		self.session = session
		self.setup_title = _("Plugin Configuration")
		Screen.__init__(self, session)
		cfg = config.plugins.xbmcplug 
                self.list = [
                        getConfigListEntry(_("Stop download at Exit from plugin ?"), cfg.tempdel),
                        getConfigListEntry(_("Cache folder"), cfg.cachefold),
                        getConfigListEntry(_("Debug log ?"), cfg.debug),
			]
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.changedEntry)
		self["status"] = Label()
		self["statusbar"] = Label()
		self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button(_("Save"))

		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
		{
			"red": self.cancel,
			"green": self.save,
			"cancel": self.cancel,
			"ok": self.save,
		}, -2)
		self.onChangedEntry = []
	
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

	def save(self):
                self.saveAll()
		self.close()



	def cancel(self):
		for x in self["config"].list:
			x[1].cancel()
                self.close()


class XbmcPlugin8(Screen):
    def __init__(self, session, name, handle):
		Screen.__init__(self, session)
		self.skinName = "xbmc3"
		self.list = []                
                self["menu"] = List(self.list)
                self["menu"] = RSList([])
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["actions"] = NumberActionMap(["OkCancelActions","DirectionActions"],{
                       "upRepeated": self.up,
                       "downRepeated": self.down,
                       "up": self.up,
                       "down": self.down,
                       "left": self.left,
                       "right":self.right,
                       "ok": self.okClicked,                                            
                       "cancel": self.cancel,}, -1)
                
                self.index = -1
                self.name = name
                self.handle = handle
                self.names = []
                self.urls = []
                self.pics = []
                self.tmppics = []
                self.lines = []
                self.vidinfo = []                
                self.data = []
                
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                system("rm /tmp/data.txt")
                self.pos = 0
                self.onShown.append(self.stream)
    
    def up(self):
                self.pos = up(self.names, self.tmppics, self.pos, self["menu"], self["pixmap"])

    def down(self):
                self.pos = down(self.names, self.tmppics, self.pos, self["menu"], self["pixmap"])
                
    def left(self):
                self.pos = left(self.names, self.tmppics, self.pos, self["menu"], self["pixmap"])

    def right(self):
                self.pos = right(self.names, self.tmppics, self.pos, self["menu"], self["pixmap"])
           
    def stream(self):
                self.index = self.index+1
                pic1 = THISPLUG + "/images/default.png"
                self["pixmap"].instance.setPixmapFromFile(pic1)
                self.picfold = config.plugins.xbmcplug.cachefold.value+"/xbmc/pic"
                self.tmpfold = config.plugins.xbmcplug.cachefold.value+"/xbmc/tmp"
#                cmd = "rm " + self.tmpfold + "/*"
#                system(cmd)
                system("rm /tmp/data.txt")
                system("rm /tmp/data.txt")
                system("rm /tmp/vidinfo.txt")
                system("rm /tmp/type.txt")
                cmd = "python " + ARG
                if DEBUG == 1:
                       print "XbmcPlugin8 self.index, ARG =", self.index, ARG
                cmd = cmd.replace("&", "\\&")
                afile = file("/tmp/test.txt","w")       
                afile.write("going in default.py")
                afile.write(cmd)
                if DEBUG == 1:
                       print "XbmcPlugin8 going in default.py cmd =", cmd
                system(cmd)
	        self.action()

    def cancel(self):
                self.close()      
	
    def keyRight(self):
		self["text"].right()
		
    def action(self):
            self.names = []
            self.urls = []
            self.pics = []
            self.names.append("Exit")
            self.urls.append(" ")
            self.pics.append(" ")
            self.tmppics = []
            self.lines = []
            self.vidinfo = []
            afile = file("/tmp/test.txt","w")       
            afile.write("\nin action=")
            datain = " "
            parameters = []
            if not path.exists("/tmp/data.txt"):
                 return
            else:
                 if not path.exists("/tmp/vidinfo.txt"):
                       pass
                 else:
                       myfile = file(r"/tmp/vidinfo.txt")       
                       icount = 0
                       vinfo = myfile.read()
                       myfile.close()
                       self.vidinfo = vinfo.split("ITEM")

                 myfile = file(r"/tmp/data.txt")       
                 icount = 0
                 for line in myfile.readlines():
                        n1 = line.find("name=", 0)
                        n2 = line.find("name=", (n1+3))
                        if n2 > -1:
                             line = line[n2:]
                        datain = line[:-1]
                        self.data.append(icount)
                        self.data[icount] = datain
                        icount = icount+1
                 myfile.close()
                 if DEBUG == 1:
                        print "XbmcPlugin8 self.data =", self.data
                 inum = icount
                 i = 0
                 while i < inum:
                        name = " "
                        url = " "
                        line = self.data[i]
                        params = parameters_string_to_dict(line)
                       
                        self.lines.append(line)
                        try:
                               name = params.get("name")
                               name = name.replace("AxNxD", "&")
                               name = name.replace("ExQ", "=")
                        except:
                               pass
                        try:
                              url = params.get("url")
                              url = url.replace("AxNxD", "&")
                              url = url.replace("ExQ", "=")
                        except:
                              pass
                        try:
                              pic = params.get("thumbnailImage")
                              if (pic == "DefaultFolder.png"):
                                     pic = THISPLUG + "/images/default.png"
                        except:
                              pic = THISPLUG + "/images/default.png" 
                        if DEBUG == 1:      
                              print "XbmcPlugin8 self.index, name =", self.index, name 
                              print "XbmcPlugin8 self.index, url =", self.index, url 
                              print "XbmcPlugin8 self.index, pic =", self.index, pic          

                        self.names.append(name)
                        self.urls.append(url)
                        self.pics.append(pic)
                        i = i+1
                 if DEBUG == 1:
                        print "XbmcPlugin8 self.names =", self.names
                        print "XbmcPlugin8 self.urls =", self.urls
                 if (len(self.names) == 2) and (self.urls[1] is None) and (THISPLUG not in self.names[1]):
                        if ("rtmp" in self.names[1]):
                            if "live" in name:
                                name = self.name
                                desc = " "
                                url = self.names[1]
#                                self.session.open(Showrtmp2, name, url, desc)
                                self.session.open(Playvid, name, url, desc)
                                self.close()
                           
                            else:
                                name = self.name
                                desc = " "
                                url = self.names[1]
                                self.session.open(Playvid, name, url, desc)
                                self.close()  
                        else:        
                                name = self.name                                
                                desc = " "
                                url = self.names[1]
                                self.session.open(Playvid, name, url, desc)
                                self.close()
                 elif (len(self.names) == 2) and (self.urls[1] is not None) and (THISPLUG not in self.urls[1]):
                        url = self.urls[1]
                        if "*download*" in url:
                                url = url.replace("*download*", "")
                                name = self.name                                
                                desc = " "
                                self.session.open(Getvid, name, url, desc)
                                self.close()
                        elif "*download2*" in url:
                                url = url.replace("*download2*", "")
                                name = self.name                                
                                desc = " "
                                self.session.open(Getvid2, name, url, desc)
                                self.close()
                        else:
                                name = self.name                                
                                desc = " "
                                self.session.open(Playvid, name, url, desc)
                                self.close()        
                                
                 else:        
                        self.tmppics = getpics(self.names, self.pics, self.tmpfold, self.picfold)
                        if DEBUG == 1:
                                print "self.names =", self.names
                                print "self.urls =", self.urls

                        showlist(self.names, self["menu"])
                        self.pos = 0
                        self["menu"].moveToIndex(self.pos) 

    def vidError(self, reply):
                return

    def okClicked(self):
          if DEBUG == 1:
                 print "In XbmcPlugin8 okClicked"
          itype = self["menu"].getSelectionIndex()
          url = self.urls[itype]
          name = self.names[itype]
          if DEBUG == 1:
                 print "In XbmcPlugin8 okClicked self.index, name =", self.index, name
                 print "In XbmcPlugin8 okClicked self.index, url =", self.index, url
          self.name = name
          if itype == 0:
                        self.close()
          else:
                if (THISPLUG not in url):
                     if ".asx" in url:
                        url1 = asxurl(url)
                        desc = " "
                        self.session.open(Playvid, name, url1, desc)
                        self.close()
                     else:           
                        desc = " "
                        self.session.open(Playvid, name, url, desc)
                        self.close()
                else:		
                        n1 = url.find('?', 0)
                        if n1<0:
                                return
                        global ARG
                        url1 = url[:n1]
                        url2 = url[n1:]
                        url2 = url2.replace(" ", "%20")
                        ARG = url1 + " 1 " + url2
		        self.stream()
		        
		        
    def keyNumberGlobal(self, number):
		self["text"].number(number)

class XbmcPlugin7(Screen):
    def __init__(self, session, names, urls, tmppics):
		Screen.__init__(self, session)
		self.skinName = "xbmc3"
             
		self.list = []                
                self["menu"] = List(self.list)
                self["menu"] = RSList([])
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["actions"] = NumberActionMap(["OkCancelActions","DirectionActions"],{
                       "upRepeated": self.up,
                       "downRepeated": self.down,
                       "up": self.up,
                       "down": self.down,
                       "left": self.left,
                       "right":self.right,
                       "ok": self.okClicked,                                            
                       "cancel": self.close,}, -1)
                self.name = "name"
                self.handle = 1
                self.names1 = names
                self.urls1 = urls
                self.tmppics1 = tmppics
                if DEBUG == 1:
                       print "XbmcPlugin7 self.names1 =", self.names1
                       print "XbmcPlugin7 self.urls1 =", self.urls1
                       print "XbmcPlugin7 self.tmppics1 =", self.tmppics1
                self.names = []
                self.urls = []
                self.pics = []
                self.tmppics = []

                self.lines = []
                self.vidinfo = []                
                self.data = []
                
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                system("rm /tmp/data.txt")
                self.pos = 0
                self.onShown.append(self.action)

    def action(self):
                        showlist(self.names1, self["menu"])
                        self.pos = 0
                        self["menu"].moveToIndex(self.pos) 
                
    def up(self):
                self.pos = up(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def down(self):
                self.pos = down(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])
                
    def left(self):
                self.pos = left(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def right(self):
                self.pos = right(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def cancel(self):
                self.close()      
	
    def keyRight(self):
		self["text"].right()
		

    def vidError(self, reply):
                return

    def okClicked(self):
          if DEBUG == 1:
                print "In XbmcPlugin7 okClicked"
          itype = self["menu"].getSelectionIndex()
          url = self.urls1[itype]
          name = self.names1[itype]
          if DEBUG == 1:
                print "XbmcPlugin7 url =", url
                print "XbmcPlugin7 name =", name
          self.name = name
          if itype == 0:
                        self.close()
          else:
                if (THISPLUG not in url):
                     if ".asx" in url:
                        url1 = asxurl(url)
                        desc = " "
                        self.session.open(Playvid, name, url1, desc)
                        self.close()
                     else:           
                        desc = " "
                        self.session.open(Playvid, name, url, desc)
                        self.close()
                else:		
                        n1 = url.find('?', 0)
                        if n1<0:
                                return
                        global ARG
                        url1 = url[:n1]
                        url2 = url[n1:]
                        url2 = url2.replace(" ", "%20")
                        ARG = url1 + " 1 " + url2
                        if DEBUG == 1:
                               print "XbmcPlugin7 ARG =", ARG
                        handle = self.handle
                        self.session.open(XbmcPlugin8, name, handle)

    def keyNumberGlobal(self, number):
		self["text"].number(number)
		
class XbmcPlugin6(Screen):
    def __init__(self, session, names, urls, tmppics):
		Screen.__init__(self, session)
		self.skinName = "xbmc3"
		self.list = []                
                self["menu"] = List(self.list)
                self["menu"] = RSList([])
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["actions"] = NumberActionMap(["OkCancelActions","DirectionActions"],{
                       "upRepeated": self.up,
                       "downRepeated": self.down,
                       "up": self.up,
                       "down": self.down,
                       "left": self.left,
                       "right":self.right,
                       "ok": self.okClicked,                                            
                       "cancel": self.cancel,}, -1)
                self.name = "name"
                self.handle = 1
                self.names1 = names
                self.urls1 = urls
                self.tmppics1 = tmppics
                if DEBUG == 1:
                       print "XbmcPlugin6 self.names1 =", self.names1
                       print "XbmcPlugin6 self.urls1 =", self.urls1
                       print "XbmcPlugin6 self.tmppics1 =", self.tmppics1
                self.names = []
                self.urls = []
                self.pics = []
                self.tmppics = []
                self.lines = []

                self.vidinfo = []                
                self.data = []
                
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                system("rm /tmp/data.txt")
                self.pos = 0
                self.onShown.append(self.action)
                
    def action(self):
                        showlist(self.names1, self["menu"])
                        self.pos = 0
                        self["menu"].moveToIndex(self.pos) 
                
    def up(self):
                self.pos = up(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def down(self):
                self.pos = down(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])
                
    def left(self):
                self.pos = left(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def right(self):
                self.pos = right(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def cancel(self):
                self.close()      
	
    def keyRight(self):
		self["text"].right()


    def vidError(self, reply):
                return

    def okClicked(self):
          if DEBUG == 1:
                print "In XbmcPlugin6 okClicked"
          itype = self["menu"].getSelectionIndex()
          url = self.urls1[itype]
          name = self.names1[itype]
          self.name = name
          if itype == 0:
                        self.close()
          else:
                  if DEBUG == 1:
                        print "In XbmcPlugin6 going in Rundefault name, url =", name, url
                  rundef = Rundefault(self.session, name, url, 7)
                  rundef.start()
                  
    def keyNumberGlobal(self, number):
		self["text"].number(number)
		
		
class XbmcPlugin5(Screen):
    def __init__(self, session, names, urls, tmppics):
		Screen.__init__(self, session)
		self.skinName = "xbmc3"
		self.list = []                
                self["menu"] = List(self.list)
                self["menu"] = RSList([])
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["actions"] = NumberActionMap(["OkCancelActions","DirectionActions"],{
                       "upRepeated": self.up,
                       "downRepeated": self.down,
                       "up": self.up,
                       "down": self.down,
                       "left": self.left,
                       "right":self.right,
                       "ok": self.okClicked,                                            
                       "cancel": self.cancel,}, -1)
                self.name = "name"
                self.handle = 1
                self.names1 = names
                self.urls1 = urls
                self.tmppics1 = tmppics
                if DEBUG == 1:
                       print "XbmcPlugin5 self.names1 =", self.names1
                       print "XbmcPlugin5 self.urls1 =", self.urls1
                       print "XbmcPlugin5 self.tmppics1 =", self.tmppics1
                self.names = []
                self.urls = []
                self.pics = []
                self.tmppics = []
                self.lines = []

                self.vidinfo = []                
                self.data = []
                
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                system("rm /tmp/data.txt")
                self.pos = 0
                self.onShown.append(self.action)
                
    def action(self):
                        showlist(self.names1, self["menu"])
                        self.pos = 0
                        self["menu"].moveToIndex(self.pos) 
                
    def up(self):
                self.pos = up(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def down(self):
                self.pos = down(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])
                
    def left(self):
                self.pos = left(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def right(self):
                self.pos = right(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def cancel(self):
                self.close()      
	
    def keyRight(self):
		self["text"].right()


    def vidError(self, reply):
                return

    def okClicked(self):
          if DEBUG == 1:
                print "In XbmcPlugin5 okClicked"
          itype = self["menu"].getSelectionIndex()
          url = self.urls1[itype]
          name = self.names1[itype]
          self.name = name
          if itype == 0:
                        self.close()
          else:
                  if DEBUG == 1:
                        print "In XbmcPlugin5 going in Rundefault name, url =", name, url
                  rundef = Rundefault(self.session, name, url, 6)
                  rundef.start()
                  
    def keyNumberGlobal(self, number):
		self["text"].number(number)
		

class XbmcPlugin4(Screen):
    def __init__(self, session, names, urls, tmppics):
		Screen.__init__(self, session)
		self.skinName = "xbmc3"
		self.list = []                
                self["menu"] = List(self.list)
                self["menu"] = RSList([])
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["actions"] = NumberActionMap(["OkCancelActions","DirectionActions"],{
                       "upRepeated": self.up,
                       "downRepeated": self.down,
                       "up": self.up,
                       "down": self.down,
                       "left": self.left,
                       "right":self.right,
                       "ok": self.okClicked,                                            
                       "cancel": self.cancel,}, -1)
                self.name = "name"
                self.handle = 1
                self.names1 = names
                self.urls1 = urls
                self.tmppics1 = tmppics
                if DEBUG == 1:
                       print "XbmcPlugin4 self.names1 =", self.names1
                       print "XbmcPlugin4 self.urls1 =", self.urls1
                       print "XbmcPlugin4 self.tmppics1 =", self.tmppics1
                self.names = []
                self.urls = []
                self.pics = []
                self.tmppics = []
                self.lines = []

                self.vidinfo = []                
                self.data = []
                
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                system("rm /tmp/data.txt")
                self.pos = 0
                self.onShown.append(self.action)
                
    def action(self):
                        showlist(self.names1, self["menu"])
                        self.pos = 0
                        self["menu"].moveToIndex(self.pos) 
                
    def up(self):
                self.pos = up(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def down(self):
                self.pos = down(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])
                
    def left(self):
                self.pos = left(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def right(self):
                self.pos = right(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def cancel(self):
                self.close()      
	
    def keyRight(self):
		self["text"].right()


    def vidError(self, reply):
                return

    def okClicked(self):
          if DEBUG == 1:
                print "In XbmcPlugin4 okClicked"
          itype = self["menu"].getSelectionIndex()
          url = self.urls1[itype]
          name = self.names1[itype]
          self.name = name
          if itype == 0:
                        self.close()
          else:
                  if DEBUG == 1:
                        print "In XbmcPlugin4 going in Rundefault name, url =", name, url
                  rundef = Rundefault(self.session, name, url, 5)
                  rundef.start()
                  
    def keyNumberGlobal(self, number):
		self["text"].number(number)


class XbmcPlugin3(Screen):
    def __init__(self, session, names, urls, tmppics):
		Screen.__init__(self, session)
		self.skinName = "xbmc3"
		self.list = []                
                self["menu"] = List(self.list)
                self["menu"] = RSList([])
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["actions"] = NumberActionMap(["OkCancelActions","DirectionActions"],{
                       "upRepeated": self.up,
                       "downRepeated": self.down,
                       "up": self.up,
                       "down": self.down,
                       "left": self.left,
                       "right":self.right,
                       "ok": self.okClicked,                                            
                       "cancel": self.cancel,}, -1)
                self.name = "name"
                self.handle = 1
                self.names1 = names
                self.urls1 = urls
                self.tmppics1 = tmppics
                if DEBUG == 1:
                       print "XbmcPlugin3 self.names1 =", self.names1
                       print "XbmcPlugin3 self.urls1 =", self.urls1
                       print "XbmcPlugin3 self.tmppics1 =", self.tmppics1
                self.names = []
                self.urls = []
                self.pics = []
                self.tmppics = []
                self.lines = []

                self.vidinfo = []                
                self.data = []
                
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                system("rm /tmp/data.txt")
                self.pos = 0
                self.onShown.append(self.action)
                
    def action(self):
                        showlist(self.names1, self["menu"])
                        self.pos = 0
                        self["menu"].moveToIndex(self.pos) 
                
    def up(self):
                self.pos = up(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def down(self):
                self.pos = down(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])
                
    def left(self):
                self.pos = left(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def right(self):
                self.pos = right(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def cancel(self):
                self.close()      
	
    def keyRight(self):
		self["text"].right()


    def vidError(self, reply):
                return

    def okClicked(self):
          if DEBUG == 1:
                print "In XbmcPlugin3 okClicked"
          itype = self["menu"].getSelectionIndex()
          url = self.urls1[itype]
          name = self.names1[itype]
          self.name = name
          if itype == 0:
                        self.close()
          else:
                  if DEBUG == 1:
                        print "In XbmcPlugin3 going in Rundefault name, url =", name, url
                  rundef = Rundefault(self.session, name, url, 4)
                  rundef.start()
                  
    def keyNumberGlobal(self, number):
		self["text"].number(number)

class XbmcPlugin2(Screen):
    def __init__(self, session, names, urls, tmppics):
		Screen.__init__(self, session)
		self.skinName = "xbmc3"
		self.list = []                
                self["menu"] = List(self.list)
                self["menu"] = RSList([])
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["actions"] = NumberActionMap(["OkCancelActions","DirectionActions"],{
                       "upRepeated": self.up,
                       "downRepeated": self.down,
                       "up": self.up,
                       "down": self.down,
                       "left": self.left,
                       "right":self.right,
                       "ok": self.okClicked,                                            
                       "cancel": self.cancel,}, -1)
                self.name = "name"
                self.handle = 1
                self.names1 = names
                self.urls1 = urls
                self.tmppics1 = tmppics
                if DEBUG == 1:
                       print "XbmcPlugin2 self.names1 =", self.names1
                       print "XbmcPlugin2 self.urls1 =", self.urls1
                       print "XbmcPlugin2 self.tmppics1 =", self.tmppics1
                self.names = []
                self.urls = []
                self.pics = []
                self.tmppics = []
                self.lines = []

                self.vidinfo = []                
                self.data = []
                
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                system("rm /tmp/data.txt")
                self.pos = 0
                self.onShown.append(self.action)
                
    def action(self):
                        showlist(self.names1, self["menu"])
                        self.pos = 0
                        self["menu"].moveToIndex(self.pos) 
                
    def up(self):
                self.pos = up(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def down(self):
                self.pos = down(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])
                
    def left(self):
                self.pos = left(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def right(self):
                self.pos = right(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def cancel(self):
                self.close()      
	
    def keyRight(self):
		self["text"].right()

    def vidError(self, reply):
                return

    def okClicked(self):
          if DEBUG == 1:
                print "In XbmcPlugin2 okClicked"
          itype = self["menu"].getSelectionIndex()
          url = self.urls1[itype]
          name = self.names1[itype]
          self.name = name
          if itype == 0:
                        self.close()
          else:
                  if DEBUG == 1:
                        print "In XbmcPlugin2 name =", name
                        print "In XbmcPlugin2 url =", url
                  rundef = Rundefault(self.session, name, url, 3)
                  rundef.start()
                  
    def keyNumberGlobal(self, number):
		self["text"].number(number)

class XbmcPlugin1(Screen):


    def __init__(self, session, name, names, urls, tmppics):
		Screen.__init__(self, session)
		self.skinName = "xbmc3"
       
		self.list = []                
                self["menu"] = List(self.list)
                self["menu"] = RSList([])
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["actions"] = NumberActionMap(["OkCancelActions", "DirectionActions"],{
                       "upRepeated": self.up,
                       "downRepeated": self.down,
                       "up": self.up,
                       "down": self.down,
                       "left": self.left,
                       "right":self.right,
                       "ok": self.okClicked,                                            
                       "cancel": self.cancel,}, -1)
                self.plug = name
                self.handle = 1
                self.names1 = names
                self.urls1 = urls
                self.tmppics1 = tmppics
                if DEBUG == 1:
                       print "XbmcPlugin1 self.names1 =", self.names1
                       print "XbmcPlugin1 self.urls1 =", self.urls1
                       print "XbmcPlugin1 self.tmppics1 =", self.tmppics1
                self.names = []
                self.urls = []
                self.pics = []
                self.tmppics = []
                self.sett = []
                self.lines = []
                self.vidinfo = []                
                self.data = []
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                system("rm /tmp/data.txt")
                self.pos = 0
                self.missed = " "
                self.shlist = " "
                self.onShown.append(self.action)


    def home(self):
                self.session.open(StartPlugin)
                self.close()

    def action(self):
                        showlist(self.names1, self["menu"])
                        self.pos = 0
                        self["menu"].moveToIndex(self.pos) 
                
    def up(self):
                self.pos = up(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def down(self):
                self.pos = down(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])
                
    def left(self):
                self.pos = left(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def right(self):
                self.pos = right(self.names1, self.tmppics1, self.pos, self["menu"], self["pixmap"])

    def cancel(self):
                self.close()      
	
    def keyRight(self):
		self["text"].right()


    def vidError(self, reply):
                return

    def okClicked(self):
          if DEBUG == 1:
                print "In XbmcPlugin1 okClicked"
          itype = self["menu"].getSelectionIndex()
          url = self.urls1[itype]
          name = self.names1[itype]
          self.name = name
          self.url = url
          if itype == 0:
                  self.close()
          elif itype == 1:
              if name == "Setup":
                  self.session.open(Addonsett, self.plug)
              else:
                  rundef = Rundefault(self.session, name, url, 2)
                  rundef.start()        
          else:
                  rundef = Rundefault(self.session, name, url, 2)
                  rundef.start()
          
class Addonsett(Screen):
    def __init__(self, session, plug):
		Screen.__init__(self, session)
		self.skinName = "xbmc3"
       
                self["menu"] = RSList([])
		self["info"] = Label()
		self["pixmap"] = Pixmap()
		self["actions"] = NumberActionMap(["OkCancelActions"],{
                       "ok": self.okClicked,                                            
                       "cancel": self.close,}, -1)
                self.plug = plug
                self.ids = []
                self.options = []
                self.types = []
                self.lnum = []
                self.ltxt = []
                self.lines = []
                self.translate()
                self.onShown.append(self.setup)

    def translate(self):
          
          path = THISPLUG + "/XBMC/" + self.plug
          if config.osd.language.value == "de_DE":
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/German"
          elif config.osd.language.value == "es_ES":
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/Spanish"       
          elif config.osd.language.value == "hj_HU":
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/Hungarian" 
          elif config.osd.language.value == "it_IT":
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/Italian"             
          else:
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/English" 
          try:
                 xfile = path + "/strings.xml"
                 tree = xml.etree.cElementTree.parse(xfile)
          except:       
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/English"
                 xfile = path + "/strings.xml"
                 tree = xml.etree.cElementTree.parse(xfile)
          root = tree.getroot()
          for string in root.iter('string'):
                  idx = string.get('id')
                  self.lnum.append(idx)
                  txtx = str(string.text)
                  self.ltxt.append(txtx) 
          return            


    def setup(self):
          pic1 = THISPLUG + "/images/default.png"
          self["pixmap"].instance.setPixmapFromFile(pic1)
          self.ids = []
          path = THISPLUG + "/XBMC/" + self.plug
          xfile = path + "/resources/settings.xml"
          f1 = open(xfile, 'r')       
          ix = 0
          for line in f1.readlines():
                 if 'type="enum"' in line: 
                        n1 = line.find("values", 0)
                        n2 = line.find('"', (n1+2))
                        n3 = line.find('"', (n2+2))
                        xval = line[(n2+1):n3]
                        self.options.append(xval)
                        n4 = line.find("label", 0)
                        n5 = line.find('"', (n4+2))
                        n6 = line.find('"', (n5+2))
                        xid = line[(n5+1):n6]
                        self.ids.append(xid)
                        self.lines.append(line)
                        ix = ix+1

                 if 'type="bool"' in line: 
                        n4 = line.find("label", 0)
                        n5 = line.find('"', (n4+2))
                        n6 = line.find('"', (n5+2))
                        xid = line[(n5+1):n6]
                        self.ids.append(xid)
                        self.lines.append(line)
                        self.options.append(" ")
                        ix = ix+1
                  
          f1.close()       
          xlen = len(self.lnum)
          xlenv = len(self.ids)  
          iv = 0
          while iv < xlenv:
                        i = 0
                        while i < xlen:
                               if self.ids[iv] == self.lnum[i]:
                                      self.ids[iv] = self.ltxt[i]
                                      break
                               i = i+1
                        iv = iv+1 

          showlist(self.ids, self["menu"])
          self["menu"].moveToIndex(0) 

    def okClicked(self):
          idx = self["menu"].getSelectionIndex()
          options = self.options[idx]
          plug = self.plug
          line = self.lines[idx]
          self.session.open(Addonsett2, plug, options, line)

class Addonsett2(Screen):
    def __init__(self, session, plug, options, line):
		Screen.__init__(self, session)
		self.skinName = "xbmc3"
                self["menu"] = RSList([])
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["actions"] = NumberActionMap(["OkCancelActions"],{
                       "ok": self.okClicked,                                            
                       "cancel": self.close,}, -1)
                self.plug = plug
                self.options = options
                self.line = line
                self.vals = []
                self.lnum = []
                self.ltxt = []
                self.translate()
                self.onShown.append(self.sel)
                
    def translate(self):
          
          path = THISPLUG + "/XBMC/" + self.plug
          if config.osd.language.value == "de_DE":
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/German"
          elif config.osd.language.value == "es_ES":
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/Spanish"       
          elif config.osd.language.value == "hj_HU":
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/Hungarian" 
          elif config.osd.language.value == "it_IT":
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/Italian"             
          else:
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/English"        
          try:
                 xfile = path + "/strings.xml"
                 tree = xml.etree.cElementTree.parse(xfile)
          except:       
                 path = THISPLUG + "/XBMC/" + self.plug + "/resources/language/English"
                 xfile = path + "/strings.xml"
                 tree = xml.etree.cElementTree.parse(xfile)

          xfile = path + "/strings.xml"
          tree = xml.etree.cElementTree.parse(xfile)
          root = tree.getroot()
          for string in root.iter('string'):
                  idx = string.get('id')
                  self.lnum.append(idx)
                  txtx = str(string.text)
                  self.ltxt.append(txtx) 
          return            

    def sel(self):
          pic1 = THISPLUG + "/images/default.png"
          self["pixmap"].instance.setPixmapFromFile(pic1)
          if 'type="bool"' in self.line:
             self.vals.append("true")
             self.vals.append("false")
          else: 
             self.vals = []
             self.vals = self.options.split("|")
             xlen = len(self.lnum)
             xlenv = len(self.vals)  
             iv = 0
             while iv < xlenv:
                        i = 0
                        while i < xlen:
                               if self.vals[iv] == self.lnum[i]:
                                      self.vals[iv] = self.ltxt[i]
                                      break
                               i = i+1
                        iv = iv+1       
         
          showlist(self.vals, self["menu"])
          self["menu"].moveToIndex(0) 

    def okClicked(self):
          isel = self["menu"].getSelectionIndex()
          if 'type="bool"' in self.line:
                  isel = self.vals[isel]
          path = THISPLUG + "/XBMC/" + self.plug
          xfile = path + "/resources/settings.xml" 
          f1 = open(xfile, 'r')
          f2 = open('/tmp/temp.xml', 'a')
          for line in f1.readlines():
                 if self.line == line:
                        n1 = line.find("default", 0)
                        n2 = line.find('"', (n1+9))
                        line = line[:(n1+9)] + str(isel) + line[n2:]
                 f2.write(line)

          f2.close()
          f1.close()  
          cmd = "mv '/tmp/temp.xml' " + xfile + " &"
          os.system(cmd)
          self.close()                   

class Rundefault(Screen):
    def __init__(self, session, name, url, nextrun):
                Screen.__init__(self, session)
                self.name = name
                self.url = url
                self.nextrun = nextrun
                self.onShown.append(self.start)
                
    def start(self):
                url = self.url
                name = self.name
                if DEBUG == 1:
                       print "In Rundefault name =", name
                       print "In Rundefault url =", url
                       print "In Rundefault self.nextrun =", self.nextrun
                if (THISPLUG not in url):
                     if ".asx" in url:
                        url1 = asxurl(url)
                        desc = " "
                        self.session.open(Playvid, name, url1, desc)
                        self.close()
                     else:           
                        desc = " "
                        self.session.open(Playvid, name, url, desc)
                        self.close()
                else:		
                        n1 = url.find('?', 0)
                        if n1<0:
                                return
                                
                        url1 = url[:n1]
                        url2 = url[n1:]
                        url2 = url2.replace(" ", "%20")        
                        arg = url1 + " 1 " + url2
                        print "Rundefault arg =", arg
                        self.arg = arg
                        self.stream()
                       
    def stream(self):

                self.picfold = config.plugins.xbmcplug.cachefold.value+"/xbmc/pic"
                self.tmpfold = config.plugins.xbmcplug.cachefold.value+"/xbmc/tmp"
#                cmd = "rm -rf " + self.tmpfold
#                system(cmd)
                system("rm /tmp/data.txt")
                system("rm /tmp/data.txt")
                system("rm /tmp/vidinfo.txt")
                system("rm /tmp/type.txt")
                if DEBUG == 1:
                       print "In rundef self.arg =", self.arg
                cmd = "python " + self.arg
                cmd = cmd.replace("&", "\\&")
                cmd = cmd.replace("(", "\\(")
                cmd = cmd.replace(")", "\\)")
                afile = file("/tmp/test.txt","w")       
                afile.write("going in default.py")
                afile.write(cmd)
                system(cmd)
	        self.action()
		
    def action(self):
            self.data = []
            self.names = []
            self.urls = []
            self.pics = []
            self.names.append("Exit")
            self.urls.append(" ")
            self.pics.append(" ")
            self.tmppics = []
            self.lines = []
            self.vidinfo = []
            afile = file("/tmp/test.txt","w")       
            afile.write("\nin action=")
            datain = " "
            parameters = []
            if not path.exists("/tmp/data.txt"):
                 return
            else:
                 if not path.exists("/tmp/vidinfo.txt"):
                       pass
                 else:
                       myfile = file(r"/tmp/vidinfo.txt")       
                       icount = 0
                       vinfo = myfile.read()
                       myfile.close()
                       self.vidinfo = vinfo.split("ITEM")
                 
                 myfile = file(r"/tmp/data.txt")       
                 icount = 0
                 for line in myfile.readlines():
                        n1 = line.find("name=", 0)
                        n2 = line.find("name=", (n1+3))
                        if n2 > -1:
                             line = line[n2:]
                        datain = line[:-1]
                        self.data.append(icount)
                        self.data[icount] = datain
                        icount = icount+1
                 myfile.close()
                 inum = icount
                 i = 0
                 while i < inum:
                        name = " "
                        url = " "
                        line = self.data[i]
                        params = parameters_string_to_dict(line)
                        if DEBUG == 1:
                               print "Rundefault params=", params
                        self.lines.append(line)
                        try:
                               name = params.get("name")
                               name = name.replace("AxNxD", "&")
                               name = name.replace("ExQ", "=")
                               if DEBUG == 1:
                                       print "Rundefault name=", name       
                        except:
                               pass
                        try:
                               url = params.get("url")
                               url = url.replace("AxNxD", "&")
                               url = url.replace("ExQ", "=")
                               if DEBUG == 1:
                                       print "Rundefault url=", url      
                        except:
                              pass
                        try:
                              pic = params.get("thumbnailImage")
                              if (pic == "DefaultFolder.png"):
                                     pic = THISPLUG + "/images/default.png"
                        except:
                              pic = THISPLUG + "/images/default.png" 
                        self.names.append(name)
                        self.urls.append(url)
                        self.pics.append(pic)
                        i = i+1
                 if DEBUG == 1:
                        print "Rundefault self.names=", self.names
                        print "Rundefault self.urls=", self.urls
                        print "Rundefault self.pics=", self.pics
                 if (len(self.names) == 2) and (self.urls[1] is None) and (THISPLUG not in self.names[1]):
                        if ("stack://" in self.names[1]):
                                stkurl = self.names[1]
                                self.playstack(stkurl)

                        elif ("rtmp" in self.names[1]):
                            if "live" in name:
                                name = self.name
                                desc = " "
                                url = self.names[1]
#                                self.session.open(Showrtmp2, name, url, desc)
                                self.session.open(Playvid, name, url, desc)
                                self.close()
                           
                            else:
                                name = self.name
                                desc = " "
                                url = self.names[1]
#                                self.session.open(Showrtmp, name, url, desc)
                                self.session.open(Playvid, name, url, desc)
                                self.close()        
                                
                        else:        
                                name = self.name                                
                                desc = " "
                                url = self.names[1]
                                self.session.open(Playvid, name, url, desc)
                                self.close()
                 elif (len(self.names) == 2) and (self.urls[1] is not None) and (THISPLUG not in self.urls[1]):
                        url = self.urls[1]
                        if "*download*" in url:
                                url = url.replace("*download*", "")
                                name = self.name                                
                                desc = " "
                                self.session.open(Getvid, name, url, desc)
                                self.close()
                        elif "*download2*" in url:
                                url = url.replace("*download2*", "")
                                name = self.name                                
                                desc = " "
                                self.session.open(Getvid2, name, url, desc)
                                self.close()
                                       
                        else:
                                name = self.name                                
                                desc = " "
                                self.session.open(Playvid, name, url, desc)
                                self.close()    
                 else:        
                        self.tmppics = getpics(self.names, self.pics, self.tmpfold, self.picfold)
                        if int(self.nextrun) == 2:
                               self.session.open(XbmcPlugin2, self.names, self.urls, self.tmppics)
                               self.close()
                        elif int(self.nextrun) == 3:
                               self.session.open(XbmcPlugin3, self.names, self.urls, self.tmppics)
                               self.close()
                        elif int(self.nextrun) == 4:
                               self.session.open(XbmcPlugin4, self.names, self.urls, self.tmppics)
                               self.close()
                        elif int(self.nextrun) == 5:
                               self.session.open(XbmcPlugin5, self.names, self.urls, self.tmppics)
                               self.close()
                        elif int(self.nextrun) == 6:
                               self.session.open(XbmcPlugin6, self.names, self.urls, self.tmppics)
                               self.close()
                        elif int(self.nextrun) == 7:
                               self.session.open(XbmcPlugin7, self.names, self.urls, self.tmppics)
                               self.close()
              
    def playstack(self, urlFull):
          if DEBUG == 1:
                 print "urlFull =", urlFull 
          playlist = []
          names = []
          i = 0
          start = 0
          while i<20:
                 n1 = urlFull.find("http", start)
                 if n1 < 0:
                        break
                 n2 = urlFull.find("http", (n1+4))
                 if n2 < 0:
                        n2 = len(urlFull)
                 url1 = urlFull[n1:n2]
#                 print "url1 =", url1 
                 n3 = url1.find(".mp4", 0)
                 if n3<0:
                        n3 = url1.find(".flv", 0)
                        if n3<0:
                              break 
                 url1 = url1[0:(n3+4)]
#                 print "url1 B=", url1
                 name = "Video" + str(i)
                 playlist.append(url1)
                 names.append(name)
#                 print "n1, n2, n3 =", n1, n2, n3
#                 print "playlist[i] =", playlist[i]
                 start = n2-1
                 i = i+1
          idx = 0       
          self.session.open(Playlist, idx, names, playlist)

    def keyNumberGlobal(self, number):
		self["text"].number(number)

class StartPlugin2(Screen):
    def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = "xbmc2"
                title = "Addons"
                self.setTitle(title)
                
                self["label1"] = StaticText("")
		self["label2"] = StaticText("")
		self["label20"] = StaticText("")
		self["label3"] = StaticText("")
		self["label30"] = StaticText("")
		self["label4"] = StaticText("")
		self["info"] = Label()
		
		self["pixmap"] = Pixmap()
		self["pixmap1"] = Pixmap()
		self.list = []                
                self["menu"] = List(self.list)
                self["menu"] = RSList([])
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["actions"] = NumberActionMap(["OkCancelActions", "ColorActions", "DirectionActions"],{
                       "upRepeated": self.up,
                       "downRepeated": self.down,
                       "up": self.up,
                       "down": self.down,
                       "left": self.left,
                       "right":self.right,
                       "red":self.close,
                       "ok": self.okClicked,                     
                       "cancel": self.close,}, -1)
                self.pos = 0
                self.num = 0
                self.urls = []
                self.names = []
                self.data = []
                self.missed = " "
                self.shlist = " "
                self.onLayoutFinish.append(self.listplugs)

    def checkImports(self):
                self.shlist = " "
                scripts = THISPLUG + "/XBMC"
                for name in os.listdir(scripts):
#                       if "script." in name:
                              self.shlist = self.shlist + name + " "
                addon = xbmcaddon.Addon(self.id)
                path = addon.getAddonInfo("path")             
                xfile = path + "/addon.xml" 
                tree = xml.etree.cElementTree.parse(xfile)
                root = tree.getroot()
                self.missed = "Please install these addons :-\n\n\n"
                i = 0
                for x in root.iter('import'):
                    addon = x.get('addon')
                    if addon == "xbmc.python":
                          continue
                    if addon in self.shlist:
                          continue
                    self.missed = self.missed + "\n" + addon
                    i = 1 
                if i == 1:
                    self.session.openWithCallback(self.error, MessageBox, self.missed, type = 3, timeout = 20)
                else:
                    arg = "'" + THISPLUG + "/XBMC/" + self.name + "/default.py' '1' ''"
                    self.arg = arg
                    self.stream()    

    def error(self, rep):
         return             

    def up(self):
         dedesc = " "
         endesc = " "
         itdesc = " "
         self["menu"].up()
         self.pos = self.pos - 1
         num = len(self.names)
         if self.pos == -1:
                self.pos = num - 1
                self["menu"].moveToIndex(self.pos) 
         name = self.names[self.pos]
         if self.pos > 4:
                pic1 = THISPLUG + "/XBMC/" + name + "/icon.png"
                self["pixmap1"].instance.setPixmapFromFile(pic1)
                pname, version, prov, desc= self.getinfo(name)
                
                self["label1"].setText(pname)
                self["label20"].setText("Version :")
                self["label2"].setText(version)
                self["label30"].setText("Provider :")
                self["label3"].setText(prov)
                self["label4"].setText(desc)
         else:      
                if self.pos == 0:
                       pic1 = THISPLUG + "/images/Exit.png"
                elif self.pos == 1:
                       pic1 = THISPLUG + "/images/Download.png"       
                elif self.pos == 2:
                       pic1 = THISPLUG + "/images/Delete.png"
                elif self.pos == 3:
                       pic1 = THISPLUG + "/images/Download.png"  
                elif self.pos == 4:
                       pic1 = THISPLUG + "/images/Download.png"  
                self["pixmap1"].instance.setPixmapFromFile(pic1)
                self["label1"].setText(" ")
                self["label20"].setText(" ")
                self["label2"].setText(" ")
                self["label30"].setText(" ")
                self["label3"].setText(" ")
                self["label4"].setText(" ")  
                
    def down(self):
         dedesc = " "
         endesc = " "
         itdesc = " "
         self["menu"].down()
         self.pos = self.pos + 1
         num = len(self.names)
         if self.pos == num:
                self.pos = 0
                self["menu"].moveToIndex(0)  
         name = self.names[self.pos]
         print "name =", name
         if self.pos > 4:
                pic1 = THISPLUG + "/XBMC/" + name + "/icon.png"
                self["pixmap1"].instance.setPixmapFromFile(pic1)
                print "name B=", name
                pname, version, prov, desc= self.getinfo(name)

                self["label1"].setText(pname)
                self["label20"].setText("Version :")
                self["label2"].setText(version)
                self["label30"].setText("Provider :")
                self["label3"].setText(prov)
                desc = desc.replace(":", "-")
                self["label4"].setText(desc)
         else:      
                if self.pos == 0:
                       pic1 = THISPLUG + "/images/Exit.png"
                elif self.pos == 1:
                       pic1 = THISPLUG + "/images/Download.png"       
                elif self.pos == 2:
                       pic1 = THISPLUG + "/images/Delete.png"
                elif self.pos == 3:
                       pic1 = THISPLUG + "/images/Download.png"  
                elif self.pos == 4:
                       pic1 = THISPLUG + "/images/Download.png"                        
                self["pixmap1"].instance.setPixmapFromFile(pic1)
                self["label1"].setText(" ")
                self["label20"].setText(" ")
                self["label2"].setText(" ")
                self["label30"].setText(" ")
                self["label3"].setText(" ")
                self["label4"].setText(" ")  
                
    def left(self):
         self["menu"].pageUp()
         self.pos = self["menu"].getSelectionIndex()
         name = self.names[self.pos]
         if self.pos > 4:
                pic1 = THISPLUG + "/XBMC/" + name + "/icon.png"
                self["pixmap1"].instance.setPixmapFromFile(pic1)
                pname, version, prov, desc = self.getinfo(name)
                
                self["label1"].setText(pname)
                self["label20"].setText("Version :")
                self["label2"].setText(version)
                self["label30"].setText("Provider :")
                self["label3"].setText(prov)
                self["label4"].setText(desc)
         else:      
                if self.pos == 0:
                       pic1 = THISPLUG + "/images/Exit.png"
                elif self.pos == 1:
                       pic1 = THISPLUG + "/images/Download.png"       
                elif self.pos == 2:
                       pic1 = THISPLUG + "/images/Delete.png"
                elif self.pos == 3:
                       pic1 = THISPLUG + "/images/Download.png"  
                elif self.pos == 4:
                       pic1 = THISPLUG + "/images/Download.png"  
                self["pixmap1"].instance.setPixmapFromFile(pic1)
                self["label1"].setText(" ")
                self["label20"].setText(" ")
                self["label2"].setText(" ")
                self["label30"].setText(" ")
                self["label3"].setText(" ")
                self["label4"].setText(" ")                        

    def right(self):
         self["menu"].pageDown()
         self.pos = self["menu"].getSelectionIndex()
         name = self.names[self.pos]
         if self.pos > 4:
                pic1 = THISPLUG + "/XBMC/" + name + "/icon.png"
                self["pixmap1"].instance.setPixmapFromFile(pic1)
                pname, version, prov, desc = self.getinfo(name)
                
                self["label1"].setText(pname)
                self["label20"].setText("Version :")
                self["label2"].setText(version)
                self["label30"].setText("Provider :")
                self["label3"].setText(prov)
                self["label4"].setText(desc)
         else:      
                if self.pos == 0:
                       pic1 = THISPLUG + "/images/Exit.png"
                elif self.pos == 1:
                       pic1 = THISPLUG + "/images/Download.png"       
                elif self.pos == 2:
                       pic1 = THISPLUG + "/images/Delete.png"
                elif self.pos == 3:
                       pic1 = THISPLUG + "/images/Download.png"  
                elif self.pos == 4:
                       pic1 = THISPLUG + "/images/Download.png"  
                self["pixmap"].instance.setPixmapFromFile(pic1)
                self["label1"].setText(" ")
                self["label20"].setText(" ")
                self["label2"].setText(" ")
                self["label30"].setText(" ")
                self["label3"].setText(" ")
                self["label4"].setText(" ") 
                                      

    def getset(self, name):            
          iset = 0
          path = THISPLUG + "/XBMC/" + self.id
          try:
                xfile = path + "/resources/settings.xml" 
                fset = open(xfile, 'r').read()
                if ('type="enum"' in fset) or ('type="bool' in fset):
                        iset = 1
                return iset
          except:
                iset = 0
                return iset                  

    def getinfo(self, name):            
                xfile = THISPLUG + "/XBMC/" + name + "/addon.xml"
                dedesc = ' '
                endesc = ' '
                itdesc = ' '
                tree = xml.etree.cElementTree.parse(xfile)
                root = tree.getroot()
                pname = str(root.get('name'))
                version = str(root.get('version'))
                prov = str(root.get('provider-name'))
                for description in root.iter('description'):
                        lang = description.get('lang')
                        desc = str(description.text)
                        if lang == "de":
                              dedesc = desc
                        elif lang == "it":
                              itdesc = desc      
                        else:      
                              endesc = desc
                              
                if config.osd.language.value == "de_DE":
                              desc2 = dedesc
                elif config.osd.language.value == "it_IT":
                              desc2 = itdesc                               
                else:
                              desc2 = endesc
                if desc2 == ' ':
                              desc2 = endesc               
                              
                return pname, version, prov, desc2
                
    def listplugs(self):
                path = THISPLUG + "/XBMC"
                self.names.append("Exit")
                self.urls.append("0")
                self.names.append("Install Addons")
                self.urls.append("0")
                self.names.append("Remove Addons")
                self.urls.append("0")
                self.names.append("Install Script-modules")
                self.urls.append("0")
                self.names.append("Install Software")
                self.urls.append("0")
                i = 1
                for name in os.listdir(path):
                    if "plugin.video" not in name:
                       continue
                    else:      
                       self.names.append(name)
                       self.urls.append(i)
                       i = i+1
                self.num = i
                showlist(self.names, self["menu"])

    def okClicked(self):
                idx = self["menu"].getSelectionIndex()
                print "idx =", idx
                if idx == 0:
                       self.close()
                elif idx == 1:
                       url ="http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/XBMCAddons/Addons/list.txt"
                       self.session.open(Addons, url)
                elif idx == 2:
                       self.session.open(DelAdd)
                       pass
                elif idx == 3:
                       url ="http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/XBMCAddons/Script-modules/list.txt"
                       self.session.open(Scripts, url)
                elif idx == 4:
                       url ="http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/XBMCAddons/Software/list.txt"
                       self.session.open(Software, url)


                else:       
		       self.name = self.names[idx]
		       self.id = self.name
		       self.checkImports()
		       
                       
    def stream(self):

                self.picfold = config.plugins.xbmcplug.cachefold.value+"/xbmc/pic"
                self.tmpfold = config.plugins.xbmcplug.cachefold.value+"/xbmc/tmp"
                cmd = "rm " + self.tmpfold + "/*"
                system(cmd)
                system("rm /tmp/data.txt")
                system("rm /tmp/data.txt")
                system("rm /tmp/vidinfo.txt")
                system("rm /tmp/type.txt")
                print "DEBUG =", DEBUG
                if DEBUG == 1:
                       print "startplugin2 self.arg =", self.arg
                cmd = "python " + self.arg
                cmd = cmd.replace("&", "\\&")
                afile = file("/tmp/test.txt","w")       
                afile.write("going in default.py")
                afile.write(cmd)
                print "going in default-py Now =", datetime.datetime.now()
                system(cmd)
	        self.action()
		
    def action(self):
            self.names2 = []
            self.urls2 = []
            self.pics2 = []
            self.names2.append("Exit")
            self.urls2.append(" ")
            self.pics2.append(" ")
            iset = 0
            iset = self.getset(self.id)
            if iset == 1:
                    self.names2.append("Setup")
                    self.urls2.append(" ")
                    self.pics2.append(" ")
            self.tmppics2 = []
            self.lines = []
            self.vidinfo = []
            afile = file("/tmp/test.txt","w")       
            afile.write("\nin action=")
            datain = " "
            parameters = []
            if not path.exists("/tmp/data.txt"):
                 return
            else:
                 if not path.exists("/tmp/vidinfo.txt"):
                       pass
                 else:
                       myfile = file(r"/tmp/vidinfo.txt")       
                       icount = 0
                       vinfo = myfile.read()
                       myfile.close()
                       self.vidinfo = vinfo.split("ITEM")
                 
                 myfile = file(r"/tmp/data.txt")       
                 icount = 0
                 for line in myfile.readlines():
                        datain = line[:-1]
                        self.data.append(icount)
                        self.data[icount] = datain
                        icount = icount+1
                 myfile.close()
                 inum = icount
                 i = 0
                 while i < inum:
                        name = " "
                        url = " "
                        line = self.data[i]
                        params = parameters_string_to_dict(line)
                        self.lines.append(line)
                        try:
                               name = params.get("name")
                               name = name.replace("AxNxD", "&")
                               name = name.replace("ExQ", "=")
                        except:
                               pass
                        try:
                              url = params.get("url")
                              url = url.replace("AxNxD", "&")
                              url = url.replace("ExQ", "=")
                        except:
                              pass
                        try:
                              pic = params.get("thumbnailImage")
                              if (pic == "DefaultFolder.png"):
                                     pic = THISPLUG + "/images/default.png"
                        except:
                              pic = THISPLUG + "/images/default.png"
                        self.name = name
                        self.names2.append(name)
                        self.urls2.append(url)
                        self.pics2.append(pic)
                        i = i+1
                 if (len(self.names2) == 2) and (self.urls2[1] is None) and (THISPLUG not in self.names2[1]):
                        if ("rtmp" in self.names2[1]):
                            if "live" in name:
                                name = self.name
                                desc = " "
                                url = self.names2[1]
#                                self.session.open(Showrtmp2, name, url, desc)
                                self.session.open(Playvid, name, url, desc)
                                self.close()
                           
                            else:
                                name = self.name
                                desc = " "
                                url = self.names[1]
#                                self.session.open(Showrtmp, name, url, desc)
                                self.session.open(Playvid, name, url, desc)
                                self.close()  

                        else:        
                                name = self.name                                
                                desc = " "
                                url = self.names2[1]
                                self.session.open(Playvid, name, url, desc)
                                self.close()
                 elif (len(self.names2) == 2) and (self.urls2[1] is not None) and (THISPLUG not in self.urls2[1]):
                                name = self.name                                
                                desc = " "
                                url = self.urls2[1]
                                self.session.open(Playvid, name, url, desc)
                                self.close()
                 else:        
                        if DEBUG == 1:
                                print "Startplugin2 self.names2 =", self.names2
                                print "Startplugin2 self.urls2 =", self.urls2
                                print "Startplugin2 self.pics2 =", self.pics2
                        self.tmppics2 = getpics(self.names2, self.pics2, self.tmpfold, self.picfold)
                        self.session.open(XbmcPlugin1, self.id, self.names2, self.urls2, self.tmppics2)
                
####################################
class Addons(Screen):

    def __init__(self, session, url):
		Screen.__init__(self, session)
#		if config.plugins.polar.menutype.value == "icons1":
#                       self.skinName = "Downloads"
#                else:       
                self.skinName = "xbmc3"
#        	self["list"] = MenuList([])
                self["menu"] = RSList([])
		self["info"] = Label()
		self.info = " "
		self.url = url
                self["info"].setText(self.info)
		self.list = []
                self["pixmap"] = Pixmap()
                self["list"] = List(self.list)
                self["list"] = RSList([])
                self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"], 
		{
			"ok": self.okClicked,
			"back": self.close,
			"red": self.close,
			"green": self.okClicked,
		}, -1)
	        self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Select"))
		title = "Plugins"
		self["title"] = Button(title)		
                self.icount = 0
                self.errcount = 0
                self.onLayoutFinish.append(self.openTest)

    def openTest(self):
                       pic1 = THISPLUG + "/images/Download.png"  
                       self["pixmap"].instance.setPixmapFromFile(pic1)
                       xurl = self.url
                       #print "xurl =", xurl
                       getPage(xurl).addCallback(self.gotPage).addErrback(self.getfeedError)

    def gotPage(self, html):
#	        try:
        	       print "html = ", html 
                       self.data = []
                       icount = 0
                       self.data = html.splitlines()

                       print "self.data here 1=", self.data
 
		       showlist(self.data, self["menu"])
		       
                       
#                except Exception, error:
#			#print "[XBMC]: Could not download HTTP Page\n" + str(error)

    def getfeedError(self, error=""):
		error = str(error)
		print "Download error =", error

    def okClicked(self):
	  if self.errcount == 1:
                self.close()
          else:      
                sel = self["menu"].getSelectionIndex()
                plug = self.data[sel]
                fdest = "/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/XBMC"
                dest = "/tmp/" + plug
                cmd1 = "wget -O '" + dest + "' 'http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/XBMCAddons/Addons/" + plug + "'"
                cmd2 = "unzip -o -q '/tmp/" + plug + "' -d " + fdest
                cmd = cmd1 + " && " + cmd2
#                print "cmd =", cmd
                title = _("Installing addons %s" %(plug))
                self.session.open(Console,_(title),[cmd])
                self.close()
                
    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()
	
    def keyNumberGlobal(self, number):
		#print "pressed", number
		self["text"].number(number)

class DelAdd(Screen):

    def __init__(self, session):
		Screen.__init__(self, session)
                self.skinName = "xbmc3"
                self["menu"] = RSList([])
		self["info"] = Label()
		self.info = " "
                self["info"].setText(self.info)
		self.list = []
                self["pixmap"] = Pixmap()
                self["list"] = List(self.list)
                self["list"] = RSList([])
                self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"], 
		{
			"ok": self.okClicked,
			"back": self.close,
			"red": self.close,
			"green": self.okClicked,
		}, -1)
	        self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Select"))
		title = "Plugins"
		self["title"] = Button(title)		
                self.icount = 0
                self.errcount = 0
                self.addlist = []
                self.onLayoutFinish.append(self.openTest)

    def openTest(self):
                       pic1 = THISPLUG + "/images/Delete.png"  
                       self["pixmap"].instance.setPixmapFromFile(pic1)
                       adds = "/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/XBMC"
                       for name in os.listdir(adds):
                              self.addlist.append(name)                      
                       shs = "/usr/lib/enigma2/python"
                       for name in os.listdir(shs):
                              if "script." in name:
                                     self.addlist.append(name) 

		       showlist(self.addlist, self["menu"])

    def okClicked(self):
                sel = self["menu"].getSelectionIndex()
                plug = self.addlist[sel]
                cmd = "rm -rf '/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/XBMC/" + plug + "'"
                title = _("Removing %s" %(plug))
                self.session.open(Console,_(title),[cmd])
                self.close()
                
    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()
	
    def keyNumberGlobal(self, number):
		self["text"].number(number)

####################################
class Scripts(Screen):

    def __init__(self, session, url):
		Screen.__init__(self, session)
#		if config.plugins.polar.menutype.value == "icons1":
#                       self.skinName = "Downloads"
#                else:       
                self.skinName = "xbmc3"
#        	self["list"] = MenuList([])
                self["menu"] = RSList([])
		self["info"] = Label()
		self.info = " "
		self.url = url
                self["info"].setText(self.info)
		self.list = []
                self["pixmap"] = Pixmap()
                self["list"] = List(self.list)
                self["list"] = RSList([])
                self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"], 
		{
			"ok": self.okClicked,
			"back": self.close,
			"red": self.close,
			"green": self.okClicked,
		}, -1)
	        self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Select"))
		title = "Plugins"
		self["title"] = Button(title)		
                self.icount = 0
                self.errcount = 0
                self.onLayoutFinish.append(self.openTest)

    def openTest(self):
                       pic1 = THISPLUG + "/images/Download.png"  
                       self["pixmap"].instance.setPixmapFromFile(pic1)
                       xurl = self.url
                       #print "xurl =", xurl
                       getPage(xurl).addCallback(self.gotPage).addErrback(self.getfeedError)

    def gotPage(self, html):
#	        try:
        	       print "html = ", html 
                       self.data = []
                       icount = 0
                       self.data = html.splitlines()

		       showlist(self.data, self["menu"])
#                except Exception, error:
#			#print "[XBMC]: Could not download HTTP Page\n" + str(error)

    def getfeedError(self, error=""):
		error = str(error)
		print "Download error =", error

    def okClicked(self):
	  if self.errcount == 1:
                self.close()
          else:      
                sel = self["menu"].getSelectionIndex()
                plug = self.data[sel]
                fdest = "/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/XBMC"
                dest = "/tmp/" + plug
                cmd1 = "wget -O '" + dest + "' 'http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/XBMCAddons/Script-modules/" + plug + "'"
                cmd2 = "unzip -o -q '/tmp/" + plug + "' -d " + fdest
                cmd = cmd1 + " && " + cmd2
#                print "cmd =", cmd
                title = _("Installing script-modules %s" %(plug))
                self.session.open(Console,_(title),[cmd])
                self.close()
                
    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()
	
    def keyNumberGlobal(self, number):
		#print "pressed", number
		self["text"].number(number)

####################################
class Software(Screen):

    def __init__(self, session, url):
		Screen.__init__(self, session)
#		if config.plugins.polar.menutype.value == "icons1":
#                       self.skinName = "Downloads"
#                else:       
                self.skinName = "xbmc3"
#        	self["list"] = MenuList([])
                self["menu"] = RSList([])
		self["info"] = Label()
		self.info = " "
		self.url = url
                self["info"].setText(self.info)
		self.list = []
                self["pixmap"] = Pixmap()
                self["list"] = List(self.list)
                self["list"] = RSList([])
                self["actions"] = NumberActionMap(["WizardActions", "InputActions", "ColorActions", "DirectionActions"], 
		{
			"ok": self.okClicked,
			"back": self.close,
			"red": self.close,
			"green": self.okClicked,
		}, -1)
	        self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Select"))
		title = "Plugins"
		self["title"] = Button(title)		
                self.icount = 0
                self.errcount = 0
                self.onLayoutFinish.append(self.openTest)

    def openTest(self):
                       pic1 = THISPLUG + "/images/Download.png"  
                       self["pixmap"].instance.setPixmapFromFile(pic1)
                       xurl = self.url
                       #print "xurl =", xurl
                       getPage(xurl).addCallback(self.gotPage).addErrback(self.getfeedError)

    def gotPage(self, html):
#	        try:
        	       print "html = ", html 
                       self.data = []
                       icount = 0
                       self.data = html.splitlines()

                       print "self.data here 1=", self.data
 
		       showlist(self.data, self["menu"])
		       
                       
#                except Exception, error:
#			#print "[XBMC]: Could not download HTTP Page\n" + str(error)

    def getfeedError(self, error=""):
		error = str(error)
		print "Download error =", error

    def okClicked(self):
	  if self.errcount == 1:
                self.close()
          else:      
                sel = self["menu"].getSelectionIndex()
                plug = self.data[sel]
                dest = "/tmp/" + plug
                cmd1 = "wget -O '" + dest + "' 'http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/XBMCAddons/Software/" + plug + "'"
                if ".ipk" in plug:
                        cmd2 = "opkg install --force-overwrite '/tmp/" + plug + "'"
                elif ".zip" in plug:        
                        cmd2 = "unzip -o -q '/tmp/" + plug + "' -d /"
                cmd = cmd1 + " && " + cmd2
#                print "cmd =", cmd
                title = _("Installing software %s" %(plug))
                self.session.open(Console,_(title),[cmd])
                self.close()
                
    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()
	
    def keyNumberGlobal(self, number):
		#print "pressed", number
		self["text"].number(number)

####################################

class StartPlugin(Screen):

        def __init__(self, session):
		Screen.__init__(self, session)
		self.skinName = "xbmc1"
                title = (_("Addons"))
                self.setTitle(title)
                self["label1"] = StaticText()
                self["label2"] = StaticText()
                self["label3"] = StaticText()
               
                self["label1s"] = StaticText()
                self["label2s"] = StaticText()
                self["label3s"] = StaticText()

                self["frame0"] = MovingPixmap()
                self["frame1"] = MovingPixmap()

        	self["list"] = MenuList([])

        	self["pixmap"] = Pixmap()
        	self["pixmap1"] = Pixmap()
		self["info"] = Label()

                self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MovieSelectionActions"],
		{
			"cancel": self.close,
			"ok": self.KeyOk,
			"left": self.key_left,
			"right": self.key_right,
			"red": self.close,
		}, -1)

                self.index = 0
       		self.pos1 = []		

                ict = 0
                i = 1280
                j = 600
                while ict < 320:
                       i1 = i
                       self.pos1.append([i1,j])
                       i = i-4
                       ict = ict+1
                self.pos2 = []		
                ict = 0
                i = 0
                j = 600
                while ict < 320:
                       i1 = i
                       self.pos2.append([i1,j])
                       i = i-4
                       ict = ict+1
                self.index0 = -1
                self.index1 = -1

                self.updateTimer = eTimer()
	    	self.updateTimer.callback.append(self.updateStatus)
		self.updateTimer.start(0400)
		self.updateStatus()
                self.onShown.append(self.openTest)
                  
        def updateStatus(self):
                   infotxt = "check ...."
                   self.index0 = self.index0+1
                   self.index1 = self.index1+1
                   self.paintFrame()

        def paintFrame(self):
                if self.index1 == 320:
		       self.index1 = 0
                if self.index0 == 320:
		       self.index0 = 0              
		
                ipos10 = self.pos1[self.index0]
		ipos11 = self.pos2[self.index1]
		self["frame0"].moveTo( ipos10[0], ipos10[1], 1)
		self["frame1"].moveTo( ipos11[0], ipos11[1], 1)
		self["frame0"].startMoving()
		self["frame1"].startMoving()
                
        def cancel(self):
                self.close()

        def openTest(self):
                self["label1"].setText(_("Addons"))
                self["label2"].setText(_("Settings"))
                self["label3"].setText(_("Exit"))
                self["label1s"].setText(" ")
                self["label2s"].setText(" ")
                self["label3s"].setText(" ")
                if self.index==0:
                        self["label1"].setText(" ")
                        self["label1s"].setText(_("Addons"))
                elif self.index==1:
                        self["label2"].setText(" ")
                        self["label2s"].setText(_("Settings"))
                elif self.index==2:
                        self["label3"].setText(" ")
                        self["label3s"].setText(_("Exit"))
               
        def key_left(self):
                self.index -= 1
                if self.index < 0:
                       self.index = 2
                self.openTest()

        def key_right(self):
		self.index += 1
		if self.index > 2:
                       self.index = 0
                self.openTest()

        def KeyOk(self):
                idx = self.index
                if idx == 0:
                       self.session.open(StartPlugin2)
                elif idx == 1:
                       self.session.open(XbmcConfigScreen) 
                elif idx == 2:
                       self.close()     
                       

class Splash(Screen):
        def __init__(self, session):
		self.skinName = "Splash"
		Screen.__init__(self, session)
                title = " "
                self.setTitle(title)
        	self["pixmap"] = Pixmap()

                self["actions"] = ActionMap(["OkCancelActions"],
		{
			"cancel": self.close,
			"ok": self.KeyOk,

		}, -1)

                self.icount = 0
                self.updateTimer = eTimer()
	    	self.updateTimer.callback.append(self.updateStatus)
		self.updateTimer.start(0400)
		self.updateStatus()
                self.onLayoutFinish.append(self.showbg)

        def showbg(self):
                   pic1 = THISPLUG + "/images/splash.png"
                   self["pixmap"].instance.setPixmapFromFile(pic1)
                   
        def updateStatus(self):
                   self.icount = self.icount+1
                   if self.icount > 10:
                           self.updateTimer.stop()
                           self.session.open(StartPlugin)
                           self.close()

        def KeyOk(self):
                       self.updateTimer.stop()
                       self.session.open(StartPlugin)
                       self.close()

def main(session, **kwargs):
        system("mkdir -p "+ config.plugins.xbmcplug.cachefold.value+"/xbmc")
        system("mkdir -p "+ config.plugins.xbmcplug.cachefold.value+"/xbmc/vid")
        system("mkdir -p "+ config.plugins.xbmcplug.cachefold.value+"/xbmc/pic")
        system("mkdir -p "+ config.plugins.xbmcplug.cachefold.value+"/xbmc/tmp")
        
        cache = config.plugins.xbmcplug.cachefold.value
        file = open("/etc/xbmc.txt", "w")
        file.write(cache)
        file.close()
       
        global DEBUG
        if config.plugins.xbmcplug.debug.value is True:
               DEBUG = 1
               f = open("/etc/debugxb", "w")
               f.close()
        else:       
               DEBUG = 0
               system('rm "/etc/debugxb"')               
               
               
######################################
        global _session 
        _session = session
        xurl = "http://www.turk-dreamworld.com/bayraklar/Receiverler/Dreambox/TDW/e2/addons/XBMCAddons/xbmc-news.txt"
        xdest = "/tmp/xbmc-news.txt"
	downloadPage(xurl, xdest).addCallback(gotNews).addErrback(showNewsError)

def showNewsError(error):
               menustart()

def gotNews(txt=" "):
                       global date
                       session = _session
                       indic = 0
                       date = ""
                       olddate = ""
                       if not os.path.exists("/tmp/xbmc-news.txt"):
                               indic = 0
                       else:
                               myfile = file(r"/tmp/xbmc-news.txt")
                               icount = 0
                               for line in myfile.readlines():
                                   if icount == 0:
                                           date = line
                                           break
                                   icount = icount+1
                               myfile.close()
                               myfile = file(r"/tmp/xbmc-news.txt")    
                               newstext = myfile.read()
                               myfile.close()
 
                       if not os.path.exists("/etc/nodlxb"):
                              indic = 1
                       else:
                              myfile2 = file(r"/etc/nodlxb")       
                              icount = 0
                              for line in myfile2.readlines():
                                    if icount == 0:
                                           olddate = line
                                           break
                                    icount = icount+1
                              if olddate != date :
                                    indic = 1
                              else:
                                    indic = 0      
                              myfile2.close()
                
                       if indic == 0:
                             menustart()
                       else:             
                             session.openWithCallback(start, MessageBox, newstext, type = 0)

def start(answer):
        if answer is not None:
                session = _session
                if answer is False:
                       file = open("/etc/nodlxb", "w")
                       file.write(date)
                       file.write("\n") 
	               file.close()

                       menustart()
                
                else:
                       os.system("rm /etc/nodlxb &")
                       menustart()
       
        else:
                       menustart()
        
def menustart():
        global date
        session = _session
#        session.open(Splash)
        session.open(StartPlugin)
        
######################################
def Plugins(**kwargs):
        loadPluginSkin(kwargs["path"])
	return PluginDescriptor(name="XBMCAddons", description="XBMC Addons for enigma2", where = PluginDescriptor.WHERE_PLUGINMENU, fnc=main)


















