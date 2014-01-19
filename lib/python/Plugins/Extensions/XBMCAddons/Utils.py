from urllib2 import urlopen
import httplib
import urlparse
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

import os
from Screens.InfoBar import MoviePlayer
from enigma import eServiceReference
from enigma import eServiceCenter

from Components.Task import Task, Job, job_manager as JobManager, Condition
from Screens.TaskView import JobView
from Components.Button import Button

from enigma import eServiceReference
from enigma import eServiceCenter
from Screens.InfoBarGenerics import *
from Screens.InfoBar import MoviePlayer, InfoBar
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

from Components.config import config

from Screens.Screen import Screen
from Tools.Directories import resolveFilename, pathExists, fileExists, SCOPE_MEDIA
from Plugins.Plugin import PluginDescriptor

from Components.Pixmap import Pixmap, MovingPixmap
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Sources.StaticText import StaticText
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch
from Components.Sources.List import List
from Components.ConfigList import ConfigList, ConfigListScreen

from Components.config import config, ConfigSubsection, ConfigInteger, ConfigSelection, ConfigText, ConfigEnableDisable, KEY_LEFT, KEY_RIGHT, KEY_0, getConfigListEntry
from Components.Task import Task, Job, job_manager as JobManager, Condition
##################
from twisted.web.client import getPage, downloadPage
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from enigma import eTimer, quitMainloop, RT_HALIGN_LEFT, RT_VALIGN_CENTER, eListboxPythonMultiContent, eListbox, gFont, getDesktop, ePicLoad
########################

from twisted.web import client
from twisted.internet import reactor
from urllib2 import Request, URLError, urlopen as urlopen2
from socket import gaierror, error
import os, socket
from urllib import quote, unquote_plus, unquote
from httplib import HTTPConnection, CannotSendRequest, BadStatusLine, HTTPException
from TaskView2 import JobViewNew

HTTPConnection.debuglevel = 1
std_headers = {
	'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Language': 'en-us,en;q=0.5',
}  
##############################################################
#                                                            #
#   Mainly Coded by pcd, July 2013                 #
#                                                            #
##############################################################
THISPLUG = "/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons"
SREF = " "

class Getvid(Screen):

    def __init__(self, session, name, url, desc):
		Screen.__init__(self, session)
#                self.skin = SkinA.skin
                self.skinName = "Showrtmp"
                title = "Play"
                self.setTitle(title)

#############################################                
		self.list = []                
                self["list"] = List(self.list)
                self["list"] = RSList([])
#############################################
		self["info"] = Label()
                self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button(_("Download"))
		self["key_yellow"] = Button(_("Play"))
		self["key_blue"] = Button(_("Stop Download"))
                self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
		{
			"red": self.close,
			"green": self.okClicked,
			"yellow": self.play,
			"blue": self.stopdl,
			"cancel": self.cancel,
			"ok": self.okClicked,
		}, -2)
                self.icount = 0
                self.name = name
                self.url = url
                txt = "Must do (1) Download  (2) Play.\n\n" + self.name + "\n\n" + desc
                self["info"].setText(txt)

                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.getrtmp)

    def getrtmp(self):
                       fold = config.plugins.xbmcplug.cachefold.value+"/xbmc/vid"
                       fname = "savedvid"
                       svfile = fold + "/" + fname + ".mpg"
                       self.svf = svfile
                       self.urtmp = "wget -O '" + svfile +"' -c '" + self.url + "'"

    def okClicked(self):
                self["info"].setText("Downloading ....")
                fold = config.plugins.xbmcplug.cachefold.value+"/xbmc/vid"
                fname = "savedvid"
                svfile = fold + "/" + fname + ".mpg"
                self.svf = svfile
                cmd = "rm " + svfile
                os.system(cmd)
                JobManager.AddJob(downloadJob(self, self.urtmp, svfile, 'Title 1')) 
                
                self.LastJobView()

 
    def LastJobView(self):
		currentjob = None
		for job in JobManager.getPendingJobs():
			currentjob = job

		if currentjob is not None:
			self.session.open(JobView, currentjob)
 
    def play(self):
          if os.path.exists(self.svf):
                #print "Showrtmp here 2"
                svfile = self.svf
                desc = " "
                self.session.open(Playvid, self.name, svfile, desc)
         
          else:      
                txt = "Download Video first."
                self["info"].setText(txt)
                
    
    def cancel(self):
	        self.session.nav.playService(self.srefOld)                
                self.close()

    def stopdl(self):
                svfile = self.svf
                cmd = "rm " + svfile
                os.system(cmd)                
                self.session.nav.playService(self.srefOld)
                cmd1 = "killall -9 rtmpdump"
                cmd2 = "killall -9 wget"
                os.system(cmd1)
                os.system(cmd2)
                self.close()

 
    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()

    def keyNumberGlobal(self, number):
		#print "pressed", number
		self["text"].number(number)

class Getvid2(Screen):

    def __init__(self, session, name, url, desc):
        global SREF
        Screen.__init__(self, session)
        self.skinName = "Showrtmp"
        self['list'] = MenuList([])
        self['info'] = Label()
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(_('Download'))
        self['key_yellow'] = Button(_('Play'))
        self['key_blue'] = Button(_('Stop Download'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'TimerEditActions'], {'red': self.close,
         'green': self.okClicked,
         'yellow': self.play,
         'blue': self.stopDL,
         'cancel': self.cancel,
         'ok': self.openTest}, -2)
        self.icount = 0
        self.bLast = 0
        cachefold = config.plugins.xbmcplug.cachefold.value
        self.svfile = cachefold + "/xbmc/vid/savedfile.mpg"
        txt = name + '\n\n\\n' + desc
        self['info'].setText(txt)
        self.updateTimer = eTimer()
        self.updateTimer.callback.append(self.updateStatus)
        self.updateTimer.start(2000)
        self.updateStatus()
        self.name = name
        self.url = url
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        SREF = self.srefOld



    def openTest(self):
        vid = self.name
        infotxt = 'Video selected :-\n\n\n' + vid
        self['info'].setText(infotxt)



    def play(self):
        desc = " "
        self.session.open(Playvid, self.name, self.url, desc)



    def play2(self):
        url = self.url
        name = self.name
        self.session.nav.stopService()
        sref = eServiceReference(4097, 0, url)
        sref.setName(name)
        self.session.nav.playService(sref)
        Screen.close(self)



    def okClicked(self):
        cmd = 'rm ' + self.svfile
        os.system(cmd)
        self.icount = 1
        JobManager.AddJob(downloadJob(self, "wget -O '" + self.svfile + "' -c '" + self.url + "'", self.svfile, 'Title 1'))



    def updateStatus(self):
        if not os.path.exists(self.svfile):
            return 
        if self.icount == 0:
            return 
        b1 = os.path.getsize(self.svfile)
        b = b1 / 1000
        if b == self.bLast:
            infotxt = 'Download Complete....' + str(b)
            self['info'].setText(infotxt)
            return 
        self.bLast = b
        infotxt = 'Downloading....' + str(b) + ' kb'
        self['info'].setText(infotxt)



    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job

        if currentjob is not None:
            self.session.open(JobView, currentjob)



    def cancel(self):
        self.session.nav.playService(SREF)
        self.close()



    def stopDL(self):
        cmd = 'killall -9 wget &'
        os.system(cmd)



    def keyLeft(self):
        self['text'].left()



    def keyRight(self):
        self['text'].right()



    def keyNumberGlobal(self, number):
        self['text'].number(number)





class Playvid(Screen, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):

    def __init__(self, session, name, url, desc):
		
		Screen.__init__(self, session)
                self.skinName = "MoviePlayer"
		title = "Play"
		self["title"] = Button(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
		InfoBarNotifications.__init__(self)
		InfoBarBase.__init__(self)
		InfoBarShowHide.__init__(self)
		self["actions"] = ActionMap(["WizardActions", "MoviePlayerActions", "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions", "InfobarShowHideActions", "InfobarActions"],
		{
			"leavePlayer":		        self.cancel,
			"back":				self.cancel,
		}, -1)

		self.allowPiP = False
		InfoBarSeek.__init__(self, actionmap = "MediaPlayerSeekActions")
                self.icount = 0
                self.name = name
                self.url = url
#ok                self.url = "rtmpe://fms-fra33.rtl.de/rtlnow/ swfVfy=1 playpath=mp4:2/V_398575_CEAT_E89903_93262_h264-mq_a535063e1a1fbf7249dbddf64452b6e6.f4v app=rtlnow/_definst_ pageUrl=http://rtl-now.rtl.de/p/ tcUrl=rtmpe://fms-fra33.rtl.de/rtlnow/ swfUrl=http://rtl-now.rtl.de/includes/vodplayer.swf"
#ok                self.url = "http://iphone.cdn.viasat.tv/iphone/008/00834/S83412_7dagemedsex_coasbb1elswjk4hj_Layer4_vod.m3u8"
                print "Here in Playvid self.url = ", self.url
                self.desc = desc
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.openTest)

    def openTest(self):                
                url = self.url
                name = self.name
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                ref = eServiceReference(0x1001, 0, url)
		ref.setName(name)
		self.session.nav.stopService()
		self.session.nav.playService(ref)
           

    def cancel(self):
                self.session.nav.stopService()
                self.session.nav.playService(self.srefOld)
#                cmd1 = "killall -9 rtmpdump"
#                cmd2 = "killall -9 wget"
#                os.system(cmd1)
#                os.system(cmd2)
                self.close()

    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()
	
    def keyNumberGlobal(self, number):
		self["text"].number(number)	

class Showrtmp(Screen):


    def __init__(self, session, name, url, desc):
		Screen.__init__(self, session)
                self.skinName = "Showrtmp"
                title = "Play"
                self.setTitle(title)
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button(_("Download"))
		self["key_yellow"] = Button(_("Play"))
		self["key_blue"] = Button(_("Stop Download"))
                self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
		{
			"red": self.close,
			"green": self.okClicked,
			"yellow": self.play,
			"blue": self.stopdl,
			"cancel": self.cancel,
			"ok": self.okClicked,
		}, -2)
                self.icount = 0
                self.name = name
                self.url = url
                txt = "Video stream rtmp.\n\n\nMust do (1) Download  (2) Play.\n\n"
                self["info"].setText(txt)
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.getrtmp)

    def getrtmp(self):
                       pic1 = THISPLUG + "/images/default.png"
                       self["pixmap"].instance.setPixmapFromFile(pic1)     
                       params = self.url
                       print "params A=", params
                       params = params.replace("-swfVfy", " --swfVfy")
                       params = params.replace("-playpath", " --playpath")
                       params = params.replace("-app", " --app")
                       params = params.replace("-pageUrl", " --pageUrl")
                       params = params.replace("-tcUrl", " --tcUrl")
                       params = params.replace("-swfUrl", " --swfUrl") 
                       print "params B=", params


                       fold = config.plugins.xbmcplug.cachefold.value + "/xbmc/vid"
                       name = self.name.replace("/media/hdd/xbmc/vid/", "")
                       name = name.replace(":", "-")
                       name = name.replace("&", "-")
                       name = name.replace(" ", "-")
                       name = name.replace("/", "-")
                       name = name.replace(".", "-")
                       self.name = name
                       svfile = fold + "/video.mpg"
                       self.svf = svfile
                       self.urtmp = "rtmpdump -r " + params + " -o '" + svfile + "'"

    def okClicked(self):
                self["info"].setText("Downloading ....")
                fold = config.plugins.xbmcplug.cachefold.value + "/xbmc/vid"
                name = self.name.replace("/media/hdd/xbmc/vid/", "")
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                name = name.replace(".", "-")
                svfile = fold + "/video.mpg"
                self.svf = svfile

                cmd = "rm " + svfile
                os.system(cmd)
                JobManager.AddJob(downloadJob(self, self.urtmp, svfile, 'Title 1')) 
                
                self.LastJobView()

 
    def LastJobView(self):
		currentjob = None
		for job in JobManager.getPendingJobs():
			currentjob = job

		if currentjob is not None:
			self.session.open(JobViewNew, currentjob)
 
    def play(self):
          if os.path.exists(self.svf):
                svfile = self.svf
                desc = " "
                self.session.open(Playvid, self.name, svfile, desc)
         
          else:      
                txt = "Download Video first."
                self["info"].setText(txt)
                
    
    def cancel(self):
	        self.session.nav.playService(self.srefOld)                
                self.close()

    def stopdl(self):
                svfile = self.svf
                cmd = "rm " + svfile
                os.system(cmd)                
                self.session.nav.playService(self.srefOld)
                cmd1 = "killall -9 rtmpdump"
                cmd2 = "killall -9 wget"
                os.system(cmd1)
                os.system(cmd2)
                self.close()

 
    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()

    def keyNumberGlobal(self, number):
		#print "pressed", number
		self["text"].number(number)

class Showrtmp2XX(Screen):
    skin = """
                <screen name="Showrtmp2" position="center,center" size="1280,720" title="  " >
                        <ePixmap position="0,0" zPosition="-2" size="1280,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/images/panel3.png" />
                        <ePixmap position="942,372" size="200,200" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/images/default.png" alphatest="on" />
                        <widget name="info" position="120,100" zPosition="4" size="500,240" font="Regular;25" foregroundColor="#ffffff" backgroundColor="#40000000" transparent="1" halign="center" valign="center" />
                        <eLabel position="150,660" zPosition="1" size="200,30" backgroundColor="#f23d21" /> 
                        <eLabel position="152,662" zPosition="1" size="196,26" backgroundColor="#40000000" /> 
                        <eLabel position="350,660" zPosition="1" size="200,30" backgroundColor="#389416" />
                        <eLabel position="352,662" zPosition="1" size="196,26" backgroundColor="#40000000" />
                        <eLabel position="550,660" zPosition="1" size="200,30" backgroundColor="#bab329" />
                        <eLabel position="552,662" zPosition="1" size="196,26" backgroundColor="#40000000" />
                        <eLabel position="750,660" zPosition="1" size="200,30" backgroundColor="#0064c7" />
                        <eLabel position="752,662" zPosition="1" size="196,26" backgroundColor="#40000000" />
                        <widget name="key_red" position="150,660" size="200,30" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> 
                        <widget name="key_green" position="350,660" size="200,30" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" /> 
                        <widget name="key_yellow" position="550,660" size="200,30" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
                        <widget name="key_blue" position="750,660" size="200,30" valign="center" halign="center" zPosition="4"  foregroundColor="#ffffff" font="Regular;20" transparent="1" shadowColor="#25062748" shadowOffset="-2,-2" />
                        <ePixmap position="100,650" zPosition="1" size="50,50" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/images/Exit2.png" />
                </screen>"""    

    def __init__(self, session, name, url, desc):
		Screen.__init__(self, session)
                self.skinName = "Showrtmp2"
                title = "Play"
                self.setTitle(title)
		self["info"] = Label()
		self["pixmap"] = Pixmap()
                self["key_red"] = Button(_("Exit"))
		self["key_green"] = Button(_("Play"))
		self["key_yellow"] = Button(_("Play"))
		self["key_blue"] = Button(_("Stop Download"))
                self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "TimerEditActions"],
		{
			"red": self.close,
			"green": self.okClicked,
			"yellow": self.play,
			"blue": self.stopdl,
			"cancel": self.cancel,
			"ok": self.okClicked,
		}, -2)
                self.icount = 0
                self.name = name
                self.url = url
                print "here in Showrtmp2"
                self.svf = " "
                self["info"].setText(str(name))
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.getrtmp)

    def getrtmp(self):
                       pic1 = THISPLUG + "/images/default.png"
                       self["pixmap"].instance.setPixmapFromFile(pic1)     
                       params = self.url
                       print "params A=", params
                       params = params.replace("swfVfy", "--swfVfy")
                       params = params.replace("playpath", "--playpath")
                       params = params.replace("app", "--app")
                       params = params.replace("pageUrl", "--pageUrl")
                       params = params.replace("tcUrl", "--tcUrl")
                       params = params.replace("swfUrl", "--swfUrl") 
                       print "params B=", params
                       
                       n1 = params.find(" ")
                       if n1<0:
                             params = "'" + params + "'"
                       else:
                             url = params[:n1]      
                             url = "'" + url + "'"
                             prest = params[n1:]
                             params = url + prest                             
                             
                       name = self.name
                       name = name.replace(":", "-")
                       name = name.replace("&", "-")
                       name = name.replace(" ", "-")
                       name = name.replace("/", "-")
                       name = name.replace(".", "-")
                       self.name = name
                       
                       if not fileExists("/tmp/vid"):
			   os.system("/usr/bin/mkfifo /tmp/vid")
 
                       local_file = "/tmp/vid"

#                       self.urtmp = "rtmpdump -v -r " + params + " -o '" + local_file + "'"
                       self.urtmp = "rtmpdump -r rtmpe://fms-fra33.rtl.de/rtlnow/ --swfVfy=1 --playpath=mp4:2/V_398575_CEAT_E89903_93262_h264-mq_a535063e1a1fbf7249dbddf64452b6e6.f4v --app=rtlnow/_definst_ --pageUrl=http://rtl-now.rtl.de/p/ --tcUrl=rtmpe://fms-fra33.rtl.de/rtlnow/ --swfUrl=http://rtl-now.rtl.de/includes/vodplayer.swf -o /tmp/vid.mpg"
                       
    def okClicked(self):
                self["info"].setText(" ")
                fold = config.plugins.xbmcplug.cachefold.value + "/xbmc/vid"
                name = self.name.replace("/media/hdd/xbmc/vid/", "")
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                name = name.replace(".", "-")

                svfile = "/tmp/vid"
                self.svf = svfile
                print "self.urtmp =", self.urtmp
#                JobManager.AddJob(downloadJob(self, self.urtmp, svfile, 'Title 1'))
                os.system(self.urtmp)

#                self.play()


    def play(self):
#         try:
                print "Showrtmp here 2"
                svfile = self.svf
#                pvd = Playvid(self.session, self.name, svfile)
                desc = " "
                self.session.open(Playvid, self.name, svfile, desc)
#                pvd.openTest()
         
#         except:       
#                return
    
    def cancel(self):
	        self.session.nav.playService(self.srefOld)                
                svfile = self.svf
                cmd = "rm " + svfile + " &"
                os.system(cmd)                
                self.session.nav.playService(self.srefOld)
                cmd1 = "killall -9 rtmpdump &"
                cmd2 = "killall -9 wget"
                os.system(cmd1)
                os.system(cmd2)
                self.close()

 
    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()

    def keyNumberGlobal(self, number):
		#print "pressed", number
		self["text"].number(number)
		


class Showrtmp2X(Screen, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):

#Now same as class Playvid 

    def __init__(self, session, name, url, desc):
		
		Screen.__init__(self, session)
                self.skinName = "MoviePlayer"
		title = "Play"
		self["title"] = Button(title)
        	self["list"] = MenuList([])
		self["info"] = Label()
		InfoBarNotifications.__init__(self)
		InfoBarBase.__init__(self)
		InfoBarShowHide.__init__(self)
		self["actions"] = ActionMap(["WizardActions", "MoviePlayerActions", "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions", "InfobarShowHideActions", "InfobarActions"],
		{
			"leavePlayer":		        self.cancel,
			"back":				self.cancel,
		}, -1)

		self.allowPiP = False
		InfoBarSeek.__init__(self, actionmap = "MediaPlayerSeekActions")
                self.icount = 0
                self.name = name
                self.url = url
                print "Here in Showrtmp2 self.url = ", self.url
                self.desc = desc
                self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
                self.onLayoutFinish.append(self.openTest)

    def openTest(self):                
                url = self.url
                name = self.name
                name = name.replace(":", "-")
                name = name.replace("&", "-")
                name = name.replace(" ", "-")
                name = name.replace("/", "-")
                ref = eServiceReference(0x1001, 0, url)
		ref.setName(name)
		self.session.nav.stopService()
		self.session.nav.playService(ref)
           

    def cancel(self):
                self.session.nav.stopService()
                self.session.nav.playService(self.srefOld)
                self.close()


    def keyLeft(self):
		self["text"].left()
	
    def keyRight(self):
		self["text"].right()
	
    def keyNumberGlobal(self, number):
		self["text"].number(number)	
		
		
		

class downloadJob(Job):
	def __init__(self, toolbox, cmdline, filename, filetitle):
		Job.__init__(self, _("Saving Video"))
		self.toolbox = toolbox
		self.retrycount = 0
                downloadTask(self, cmdline, filename, filetitle)

	def retry(self):
		assert self.status == self.FAILED
		self.retrycount += 1
		self.restart()
	
class downloadTask(Task):
	ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = range(5)
	def __init__(self, job, cmdline, filename, filetitle):
		Task.__init__(self, job, filetitle)
                self.setCmdline(cmdline)
		self.filename = filename
		self.toolbox = job.toolbox
		self.error = None
		self.lasterrormsg = None
		
	def processOutput(self, data):
		try:
			if data.endswith('%)'):
				startpos = data.rfind("sec (")+5
				if startpos and startpos != -1:
					self.progress = int(float(data[startpos:-4]))
			elif data.find('%') != -1:
				tmpvalue = data[:data.find("%")]
				tmpvalue = tmpvalue[tmpvalue.rfind(" "):].strip()
				tmpvalue = tmpvalue[tmpvalue.rfind("(")+1:].strip()
				self.progress = int(float(tmpvalue))
			else:
				Task.processOutput(self, data)
		except Exception, errormsg:
			Task.processOutput(self, data)

	def processOutputLine(self, line):
			self.error = self.ERROR_SERVER
			
	def afterRun(self):
		pass


class RSList(MenuList):
	def __init__(self, list):
		MenuList.__init__(self, list, False, eListboxPythonMultiContent)
		self.l.setItemHeight(40)
		self.l.setFont(0, gFont("Regular", 25))

def RSListEntry(download):
	res = [(download)]

        white = 0xffffff 
        grey = 0xb3b3b9
        green = 0x389416
        black = 0x000000
        yellow = 0xe5b243

        res.append(MultiContentEntryText(pos=(0, 0), size=(650, 40), text=download, color=grey, color_sel = white, backcolor = black, backcolor_sel = black))
        return res

def showlist(data, list):                   
                       icount = 0
                       plist = []
                       for line in data:
                               name = data[icount]                               
                               plist.append(RSListEntry(name))                               
                               icount = icount+1

		       list.setList(plist)


#################                

class Playlist(Screen, InfoBarBase, InfoBarSeek, InfoBarNotifications, InfoBarShowHide):
	ENABLE_RESUME_SUPPORT = True
	ALLOW_SUSPEND = True
		
	def __init__(self, session, idx, names, playlist):
		Screen.__init__(self, session)
		self.session = session

		InfoBarNotifications.__init__(self)
		InfoBarBase.__init__(self)
		InfoBarShowHide.__init__(self)

		self["actions"] = ActionMap(["WizardActions", "MoviePlayerActions", "EPGSelectActions", "MediaPlayerSeekActions", "ColorActions", "InfobarShowHideActions", "InfobarActions"],
		{
			"leavePlayer":		        self.leavePlayer,
			"back":				self.leavePlayer,
			"left":				self.previous,
			"right":			self.next,
#			"info":				self.lyrics,
#			"up":				self.playlist,
			"down":				self.random_now,
#			"input_date_time":	        self.playconfig,
#			"menu":	                        self.playconfig,

		}, -1)

		self.allowPiP = False
		InfoBarSeek.__init__(self, actionmap = "MediaPlayerSeekActions")

		self.returning = False
		self.skinName = "MoviePlayer"
		self.lastservice = session.nav.getCurrentlyPlayingServiceReference()

#		self.filename = filename
		self.playlist = playlist
#		print "playlist = ", playlist
		self.names = names
		self.index = idx
		####print self.index

              
                self.mrl = " "

		self.onLayoutFinish.append(self.play)

	def play(self):
		    self.onClose.append(self.__onClose)
     
                    vidid = -1
                    for video in self.playlist:
		         vidid = vidid+1
                         ####print "video =", video
                         if vidid == int(self.index):
					self.url = video
                                        self.name = self.names[self.index]
                                        vurl = self.url        
                                        ####print "vurl =", vurl
					try:
					       ref = eServiceReference(0x1001, 0, vurl)
					       ref.setName(self.name)
					       self.session.nav.stopService()
					       self.session.nav.playService(ref)
					except:
                                               continue

	def leavePlayer(self):
                self.close()

	def next(self):
		self.index += 1
		if len(self.chartList) < self.index -1:
			self.index = 1
			self.play()
		else:
			self.play()

	def previous(self):
		####print "previous Song"
		self.index -= 1
		####print self.index
		if int(self.index) == int(0):
			self.index = len(self.chartList)
			self.play()
		else:
			self.play()

	def random_now(self):
		####print "Random now:", self.index
		self.index = random.randint(1, len(self.chartList))
		####print "Random create:", self.index
		self.play()

	def doEofInternal(self, playing):		
			os.system("sleep 4")
                        ####print "next song now:", self.index
                        if self.index == (len(self.playlist)-1):
                                 self.index = -1
			self.index += 1
			####print "next song create:", self.index
			if len(self.playlist) < self.index -1:
				self.close()
			else:
				self.play()
                                self.hide()		

	def doEofInternal3(self, playing):		
		####print "current song:", self.index
		if int(self.random) == int(1):
			####print "Random now:", self.index
			self.index = random.randint(1, len(self.chartList))
			####print "Random create:", self.index
			self.play()

		elif int(self.repeat) == int(1):
			####print "Repeat now:", self.index
			self.play()
		        self.hide()
                else:
			####print "next song now:", self.index
			self.index += 1
			####print "next song create:", self.index
			if len(self.chartList) < self.index -1:
				self.close()
			else:
				self.play()
                                self.hide()
		
		

                                
	def __onClose(self):
                self.session.nav.playService(self.lastservice)
#                self.close()

        def yturl(self):
           start = 0
           ####print "getvlc self.url =", self.url
           pos1 = self.url.find("=", start)
#           pos2 = self.url.find("&", pos1+2)
           self.vid = self.url[(pos1+1):]
           #####print "self.vid =", self.vid
#           try:
           self.mrl = self.getVideoUrl()
#           except:
#                   return        
           #####print "self.mrl = ", self.mrl
           self.name = self.name.replace("_", " ").replace("_", " ")
           return self.mrl
                
        def getVideoUrl(self):
                video_url = None
		video_id = self.vid
		watch_url = 'http://www.youtube.com/watch?v=%s&gl=US&hl=en' % video_id
		watchrequest = Request(watch_url, None, std_headers)
		try:
			######print "[MyTube] trying to find out if a HD Stream is available",watch_url
			watchvideopage = urlopen(watchrequest).read()
			#####print "[MyTube] watchvideopage =", watchvideopage
		except (URLError, HTTPException, socket.error), err:
			######print "[MyTube] Error: Unable to retrieve watchpage - Error code: ", str(err)
			######print "[MyTube] video_url A =", video_url
                        return video_url
		
		fpage = watchvideopage
		pos1 = fpage.find('yt.preload.start(', 0)
                if (pos1 < 0):
                        return video_url
                pos2 = fpage.find('yt.preload.start(', (pos1+2))
                if (pos2 < 0):
                        return video_url
                pos3 = fpage.find(')', (pos2+5))
                if (pos3 < 0):
                        return video_url
                        
                url = fpage[(pos2+18):(pos3-1)]
                url = url.replace('\u0026', '&')
                url = url.replace("\\", '')
                url = url.replace('%2C', ',')                        
                url = url.replace('generate_204', 'videoplayback')        
		video_url = url
		return video_url
               
#######################################    





















































































