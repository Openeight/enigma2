#
#  sundtek control center
#  coded by giro77
#  support: http://www.i-have-a-dreambox.com
#
#  Sundtek:
#  - reworked support for multiple tuners
#  - fixed device selection
#  - updated networking support
#
#  This plugin is licensed under the Creative Commons
#  Attribution-NonCommercial-ShareAlike 3.0 Unported License.
#  To view a copy of this license, please visit
#  http://creativecommons.org/licenses/by-nc-sa/3.0/ or send a letter to Creative
#  Commons, 559 Nathan Abbott Way, Stanford, California 94305, USA.
#
#  Alternatively, this plugin may be distributed
#  with devices from sundtek ltd. or sundtek germany.
#
#
#  Sundtek Control Center Plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#

from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry, ConfigNothing, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, ConfigSelection, configfile
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.NimManager import nimmanager
from enigma import eConsoleAppContainer, getDesktop
from Screens.ChoiceBox import ChoiceBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.Console import Console
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
import six
if six.PY3:
	from urllib.request import urlopen
else: # Python 2
	from urllib2 import urlopen
import os
import re
import time
import datetime
import array
import struct
import fcntl
from threading import Thread
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SHUT_RDWR
SIOCGIFCONF = 0x8912
BYTES = 4096

# for localized texts
from . import _

## configs ################################################################

device_choices = []
device_choices_whitelist = []
device_choices_blacklist = []

config.plugins.SundtekControlCenter = ConfigSubsection()

vtuner_interfaces = []
vtuner_dir = "/dev/misc/"
if not os.path.isdir(vtuner_dir):
	vtuner_dir = "/dev/"
for dirname, dirnames, filenames in os.walk(vtuner_dir):
	for filename in filenames:
		if (len(filename) >= 7) and (filename[0:6] == "vtuner"):
			vtuner_interfaces.append(filename)

vtuner_nifs = len(vtuner_interfaces)

sundtek_devices = {}

# Enigma2 does not support arrays within the configuration class so we need to add members dynamically

for i in range(0, vtuner_nifs):
	config.plugins.SundtekControlCenter.__dict__["tuner_enabled_%d" % i] = ConfigYesNo(default=False)
	config.plugins.SundtekControlCenter.__dict__["devices_%d" % i] = ConfigNothing()
	config.plugins.SundtekControlCenter.__dict__["dvbtransmission1_%d" % i] = ConfigNothing()

config.plugins.SundtekControlCenter.display = ConfigSelection(default="1", choices=[("0", _("nowhere")), ("1", _("extension menu")), ("2", _("scan menu")), ("3", _("extension/scan menu"))])
config.plugins.SundtekControlCenter.scanNetwork = ConfigNothing()
config.plugins.SundtekControlCenter.networkIp = ConfigText(default="0.0.0.0", visible_width=50, fixed_size=False)
config.plugins.SundtekControlCenter.sunconf = ConfigSubsection()
config.plugins.SundtekControlCenter.sunconf.support = ConfigSelection(default="0", choices=[("0", _("hide")), ("1", _("show"))])
config.plugins.SundtekControlCenter.sunconf.autostart = ConfigYesNo(default=False)
config.plugins.SundtekControlCenter.sunconf.autoupdate = ConfigYesNo(default=False)
config.plugins.SundtekControlCenter.sunconf.vtuneracceleration = ConfigYesNo(default=False)
config.plugins.SundtekControlCenter.sunconf.searchversion = ConfigYesNo(default=False)

orginal_dmm = False
if not os.path.exists("/proc/stb/info/boxtype") and os.path.exists("/proc/stb/info/model") and config.plugins.SundtekControlCenter.sunconf.searchversion.value:
	config.plugins.SundtekControlCenter.sunconf.searchversion.value = False
	config.plugins.SundtekControlCenter.sunconf.searchversion.save()
	orginal_dmm = True
config.plugins.SundtekControlCenter.sunconf.loglevel = ConfigSelection(default="0", choices=[("0", _("off")), ("1", _("min")), ("2", _("max"))])
config.plugins.SundtekControlCenter.sunconf.dmhwpidfilter = ConfigSelection(default="1", choices=[("0", _("off")), ("1", _("on"))])
config.plugins.SundtekControlCenter.sunconf.networkmode = ConfigSelection(default="0", choices=[("0", _("off")), ("1", _("on"))])

## version string #########################################################

sundtekcontrolcenter_version = "20210624-2"
testOK = None

###########################################################################


class SundtekControlCenter(Screen, ConfigListScreen):
	nims = nimmanager.nimList() # get nim_sockets
	result = []
	config_list = {}
	for item in nims:
		if _('Sundtek') in item and (_('DVB-') in item or _('ATSC') in item):
			result.append((item))
	imageone = ""
	imagetwo = ""
	framewidth = getDesktop(0).size().width()
	if framewidth >= 1024:
		if len(result) == 1:
			if (_("ATSC") in result[0]) or (_("DVB-C") in result[0]) or (_("DVB-T2") in result[0]) or (_("DVB-T2") in result[0]):
				imageone = "/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/sundtek_dvbc.png"
			else:
				imageone = "/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/sundtek_dvbs.png"
			skin = "<screen title=\"SundtekControlCenter\" position=\"center,center\" size=\"750,550\" name=\"SundtekControlCenter\">\
				<ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/pics/bg.png\" position=\"0,0\" size=\"750,124\" alphatest=\"on\"/>\
				<ePixmap pixmap=\"skin_default/buttons/red.png\" position=\"75,385\" size=\"140,40\" alphatest=\"on\"/>\
				<ePixmap pixmap=\"skin_default/buttons/green.png\" position=\"225,385\" size=\"140,40\" alphatest=\"on\"/>\
				<ePixmap pixmap=\"skin_default/buttons/yellow.png\" position=\"375,385\" size=\"140,40\" alphatest=\"on\"/>\
				<ePixmap pixmap=\"skin_default/buttons/blue.png\" position=\"525,385\" size=\"140,40\" alphatest=\"on\"/>\
				<widget name=\"btt_red\" position=\"75,385\" zPosition=\"1\" size=\"140,40\" font=\"Regular;17\" halign=\"center\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"btt_green\" position=\"225,385\" zPosition=\"1\" size=\"140,40\" font=\"Regular;17\" halign=\"center\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"btt_yellow\" position=\"375,385\" zPosition=\"1\" size=\"140,40\" font=\"Regular;17\" halign=\"center\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"btt_blue\" position=\"525,385\" zPosition=\"1\" size=\"140,40\" font=\"Regular;17\" halign=\"center\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"ok\" position=\"25,430\" zPosition=\"1\" size=\"630,40\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"menu\" position=\"25,450\" zPosition=\"1\" size=\"630,40\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"infos\" position=\"25,470\" zPosition=\"1\" size=\"630,40\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"bouquets\" position=\"25,490\" zPosition=\"1\" size=\"630,40\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"netservers\" position=\"25,510\" zPosition=\"1\" size=\"630,40\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"driverupdateavail\" position=\"375,37\" zPosition=\"1\" size=\"350,30\" font=\"Regular;16\" halign=\"right\" valign=\"center\" transparent=\"1\" shadowColor=\"black\" shadowOffset=\"-3,-3\" foregroundColor=\"#00ffffff\"/>\
				<widget name=\"updateavail\" position=\"375,55\" zPosition=\"1\" size=\"350,30\" font=\"Regular;16\" halign=\"right\" valign=\"center\" transparent=\"1\" shadowColor=\"black\" shadowOffset=\"-3,-3\" foregroundColor=\"#00ffffff\"/>\
				<widget name=\"version\" position=\"575,75\" zPosition=\"1\" size=\"150,30\" font=\"Regular;16\" halign=\"right\" valign=\"center\" transparent=\"1\" shadowColor=\"black\" shadowOffset=\"-3,-3\"/>\
				<widget name=\"config\" position=\"240,135\" size=\"480,250\" scrollbarMode=\"showOnDemand\" zPosition=\"1\"/>\
				<ePixmap position=\"35,130\" size=\"96,58\" pixmap=\"" + imageone + "\" transparent=\"1\" alphatest=\"on\"/>\
				<widget name=\"tunerone\" position=\"25,190\" zPosition=\"1\" size=\"215,60\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<ePixmap position=\"625, 500\" size=\"100,40\" pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/sundtek.png\" transparent=\"1\" alphatest=\"on\"/>\
			</screen>"
		elif len(result) >= 2:
			if (_("ATSC") in result[0]) or (_("DVB-C") in result[0]) or (_("DVB-T2") in result[0]) or (_("DVB-T2") in result[0]):
				imageone = "/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/sundtek_dvbc.png"
			else:
				imageone = "/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/sundtek_dvbs.png"
			if (_("ATSC") in result[0]) or (_("DVB-C") in result[1]) or (_("DVB-T2") in result[1]) or (_("DVB-T2") in result[1]):
				imagetwo = "/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/sundtek_dvbc.png"
			else:
				imagetwo = "/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/sundtek_dvbs.png"
			skin = "<screen title=\"SundtekControlCenter\" position=\"center,center\" size=\"750,550\" name=\"SundtekControlCenter\">\
				<ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/pics/bg.png\" position=\"0,0\" size=\"750,124\" alphatest=\"on\"/>\
				<ePixmap pixmap=\"skin_default/buttons/red.png\" position=\"75,385\" size=\"140,40\" alphatest=\"on\"/>\
				<ePixmap pixmap=\"skin_default/buttons/green.png\" position=\"225,385\" size=\"140,40\" alphatest=\"on\"/>\
				<ePixmap pixmap=\"skin_default/buttons/yellow.png\" position=\"375,385\" size=\"140,40\" alphatest=\"on\"/>\
				<ePixmap pixmap=\"skin_default/buttons/blue.png\" position=\"525,385\" size=\"140,40\" alphatest=\"on\"/>\
				<widget name=\"btt_red\" position=\"75,385\" zPosition=\"1\" size=\"140,40\" font=\"Regular;17\" halign=\"center\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"btt_green\" position=\"225,385\" zPosition=\"1\" size=\"140,40\" font=\"Regular;17\" halign=\"center\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"btt_yellow\" position=\"375,385\" zPosition=\"1\" size=\"140,40\" font=\"Regular;17\" halign=\"center\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"btt_blue\" position=\"525,385\" zPosition=\"1\" size=\"140,40\" font=\"Regular;17\" halign=\"center\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"ok\" position=\"25,430\" zPosition=\"1\" size=\"630,40\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"menu\" position=\"25,450\" zPosition=\"1\" size=\"630,40\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"infos\" position=\"25,470\" zPosition=\"1\" size=\"630,40\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"bouquets\" position=\"25,490\" zPosition=\"1\" size=\"630,40\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"netservers\" position=\"25,510\" zPosition=\"1\" size=\"630,40\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<widget name=\"driverupdateavail\" position=\"375,37\" zPosition=\"1\" size=\"350,30\" font=\"Regular;16\" halign=\"right\" valign=\"center\" transparent=\"1\" shadowColor=\"black\" shadowOffset=\"-3,-3\" foregroundColor=\"#00ffffff\"/>\
				<widget name=\"updateavail\" position=\"375,55\" zPosition=\"1\" size=\"350,30\" font=\"Regular;16\" halign=\"right\" valign=\"center\" transparent=\"1\" shadowColor=\"black\" shadowOffset=\"-3,-3\" foregroundColor=\"#00ffffff\"/>\
				<widget name=\"version\" position=\"575,75\" zPosition=\"1\" size=\"150,30\" font=\"Regular;16\" halign=\"right\" valign=\"center\" transparent=\"1\" shadowColor=\"black\" shadowOffset=\"-3,-3\"/>\
				<widget name=\"config\" position=\"240,135\" size=\"480,250\" scrollbarMode=\"showOnDemand\" zPosition=\"1\"/>\
				<ePixmap position=\"35,130\" size=\"96,58\" pixmap=\"" + imageone + "\" transparent=\"1\" alphatest=\"on\"/>\
				<widget name=\"tunerone\" position=\"25,190\" zPosition=\"1\" size=\"215,60\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<ePixmap position=\"35,255\" size=\"96,58\" pixmap=\"" + imagetwo + "\" transparent=\"1\" alphatest=\"on\"/>\
				<widget name=\"tunertwo\" position=\"25,315\" zPosition=\"1\" size=\"215,68\" font=\"Regular;16\" halign=\"left\" valign=\"center\" shadowColor=\"black\" shadowOffset=\"-1,-1\" transparent=\"1\"/>\
				<ePixmap position=\"625, 500\" size=\"100,40\" pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/sundtek.png\" transparent=\"1\" alphatest=\"on\"/>\
			</screen>"
		else:
			skin = """
			<screen title="SundtekControlCenter" position="center,center" size="750,550" name="SundtekControlCenter">
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/pics/bg.png" position="0,0" size="750,124" alphatest="on"/>
				<ePixmap pixmap="skin_default/buttons/red.png" position="75,385" size="140,40" alphatest="on"/>
				<ePixmap pixmap="skin_default/buttons/green.png" position="225,385" size="140,40" alphatest="on"/>
				<ePixmap pixmap="skin_default/buttons/yellow.png" position="375,385" size="140,40" alphatest="on"/>
				<ePixmap pixmap="skin_default/buttons/blue.png" position="525,385" size="140,40" alphatest="on"/>
				<widget name="btt_red" position="75,385" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
				<widget name="btt_green" position="225,385" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
				<widget name="btt_yellow" position="375,385" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
				<widget name="btt_blue" position="525,385" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
				<widget name="ok" position="25,430" zPosition="1" size="630,40" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
				<widget name="menu" position="25,450" zPosition="1" size="630,40" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
				<widget name="infos" position="25,470" zPosition="1" size="630,40" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
				<widget name="bouquets" position="25,490" zPosition="1" size="630,40" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
				<widget name="netservers" position="25,510" zPosition="1" size="630,40" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
				<widget name="driverupdateavail" position="375,37" zPosition="1" size="350,30" font="Regular;16" halign="right" valign="center" transparent="1" shadowColor="black" shadowOffset="-3,-3" foregroundColor="#00ffffff"/>
				<widget name="updateavail" position="375,55" zPosition="1" size="350,30" font="Regular;16" halign="right" valign="center" transparent="1" shadowColor="black" shadowOffset="-3,-3" foregroundColor="#00ffffff"/>
				<widget name="version" position="575,75" zPosition="1" size="150,30" font="Regular;16" halign="right" valign="center" transparent="1" shadowColor="black" shadowOffset="-3,-3"/>
				<widget name="config" position="240,135" size="480,245" scrollbarMode="showOnDemand" zPosition="1"/>
				<widget name="tunerone" position="25,190" zPosition="1" size="215,60" font="Regular;16" halign="center" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
				<ePixmap position="625, 500" size="100,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/sundtek.png" transparent="1" alphatest="on"/>
			</screen>"""
	else:
		skin = """
		<screen title="SundtekControlCenter" position="40,60" size="620,480" name="SundtekControlCenter">
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/pics/bg_sd.png" position="0,0" size="620,93" alphatest="on"/>
			<ePixmap pixmap="skin_default/buttons/red.png" position="10,320" size="140,40" alphatest="on"/>
			<ePixmap pixmap="skin_default/buttons/green.png" position="160,320" size="140,40" alphatest="on"/>
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="310,320" size="140,40" alphatest="on"/>
			<ePixmap pixmap="skin_default/buttons/blue.png" position="460,320" size="140,40" alphatest="on"/>
			<widget name="btt_red" position="10,320" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
			<widget name="btt_green" position="160,320" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
			<widget name="btt_yellow" position="310,320" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
			<widget name="btt_blue" position="460,320" zPosition="1" size="140,40" font="Regular;17" halign="center" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
			<widget name="ok" position="25,370" zPosition="1" size="630,40" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
			<widget name="menu" position="25,390" zPosition="1" size="630,40" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
			<widget name="infos" position="25,410" zPosition="1" size="630,40" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
			<widget name="bouquets" position="25,430" zPosition="1" size="630,40" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
			<widget name="netservers" position="25,450" zPosition="1" size="630,40" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
			<widget name="driverupdateavail" position="245,30" zPosition="1" size="350,30" font="Regular;16" halign="right" valign="center" transparent="1" shadowColor="black" shadowOffset="-3,-3" foregroundColor="#00ffffff"/>
			<widget name="updateavail" position="245,50" zPosition="1" size="350,30" font="Regular;16" halign="right" valign="center" transparent="1" shadowColor="black" shadowOffset="-3,-3" foregroundColor="#00ffffff"/>
			<widget name="version" position="445,10" zPosition="1" size="150,30" font="Regular;16" halign="right" valign="center" transparent="1" shadowColor="black" shadowOffset="-3,-3"/>
			<widget name="config" position="25,100" size="570,200" scrollbarMode="showOnDemand" zPosition="1"/>
			<widget name="tunerone" position="25,10" zPosition="1" size="215,60" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
			<widget name="tunertwo" position="220,10" zPosition="1" size="215,68" font="Regular;16" halign="left" valign="center" shadowColor="black" shadowOffset="-1,-1" transparent="1"/>
			<ePixmap position="495, 410" size="100,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/icons/sundtek.png" transparent="1" alphatest="on"/>
		</screen>"""

	def readConfig(self):
		self.config_list = {}
		fh = None
		try:
			fh = open("/etc/sundtek.conf", "r")
		except:
			return
		conf = fh.read()
		sections = conf.split("[")
		d = 0
		e = 0
		for i in sections:
			# 0 is global section
			if (d > 0):
				# if it's not the network section proceed
				if i[0:8] != "NETWORK]":
					serial = i[0:i.find("]")]
					if "/1" in serial:
						continue
					nr = i.find("netrecoverymode=on")
					if (nr > 0):
						nr_enabled = True
					else:
						nr_enabled = False

					dse = i.find("dreambox_support_fe1=on")
					if (dse > 0):
						fe_enabled = True
					else:
						fe_enabled = False

					initial_mode = ""
					idm = i.find("initial_dvb_mode=DVBT2")
					if (idm > 0):
						initial_mode = "DVB-T2"
					else:
						idm = i.find("initial_dvb_mode=DVBT")
						if (idm > 0):
							initial_mode = "DVB-T"
						else:
							idm = i.find("initial_dvb_mode=DVBC")
							if (idm > 0):
								initial_mode = "DVB-C"

					self.config_list[e] = {}
					self.config_list[e]['serial'] = serial

					self.config_list[e]['enabled'] = fe_enabled

					self.config_list[e]['initial_mode'] = initial_mode
					e = e + 1

			d = d + 1

	def updateDefaults(self):
		global vtuner_nifs, sundtek_devices, device_choices_whitelist
		if (len(self.config_list) > 0):
			for i in range(0, vtuner_nifs):
				config.plugins.SundtekControlCenter.__dict__["tuner_enabled_%d" % i].value = False
				for b in sundtek_devices:
					if i in list(self.config_list.keys()):
						if (sundtek_devices[b]['serial'] == self.config_list[i]['serial']):
							idx = b
							config.plugins.SundtekControlCenter.__dict__["devices_%d" % i] = ConfigSelection(default='%d' % idx, choices=list(device_choices))

							config.plugins.SundtekControlCenter.__dict__["tuner_enabled_%d" % i].value = True
							if 'initial_mode' in list(self.config_list[i].keys()):
								n = 0
								for c in sundtek_devices[b]['capabilities']:
									if c[1] == self.config_list[i]['initial_mode']:
										config.plugins.SundtekControlCenter.__dict__["dvbtransmission1_%d" % i] = ConfigSelection(default='%d' % n, choices=sundtek_devices[b]['capabilities'])
										break
									n = n + 1

	def __init__(self, session, args=0):
		global sundtek_devices
		Screen.__init__(self, session)
		ConfigListScreen.__init__(self, [])
		### get nim_socket informations
		result = []
		i = 0
		nims = nimmanager.nimList()
		for item in nims:
			if _('Sundtek') in item and (_('DVB-') in item or _('ATSC') in item):
				result.append((item))
				i += 1
		self.total = i
		self.network = False
		self.updateDeviceList()
		self.readConfig()
		self.updateDefaults()
		self.updateSettingList()
		self["key_red"] = self["btt_red"] = Label(_("Exit"))
		self["key_green"] = self["btt_green"] = Label(_("Save setup"))
		self["key_yellow"] = self["btt_yellow"] = Label(_("Restart"))
		self["key_blue"] = self["btt_blue"] = Label(_("Save and start tuner"))
		self["ok"] = Label(_("OK/ green = activate settings"))
		self["menu"] = Label(_("Menu = call further functions..."))
		self["infos"] = Label(_("Info = show tuner informations"))
		self["bouquets"] = Label(_("Bouquet + = install or update driver"))
		self["netservers"] = Label(_("Bouquet - = scan for IPTV server addresses"))
		self["version"] = Label(sundtekcontrolcenter_version)
		self["tunerone"] = Label("")
		self["tunertwo"] = Label("")
		self["updateavail"] = Label("")
		if os.path.exists("/opt/bin/mediaclient"):
			self["driverupdateavail"] = Label("")
		else:
			self["driverupdateavail"] = Label("n/a")

		### get tunerinformations
		# just for fun, the tuner configuration
		ntuners = len(sundtek_devices)
		if ntuners > 0:
			tunertwo = ""
			for i in sundtek_devices:
				if i == 0:
					self["tunerone"] = Label(six.ensure_str(sundtek_devices[0]['device'])[2:])
				elif i == 1:
					tunertwo = six.ensure_str(sundtek_devices[1]['device'][2:])
				else:
					tunertwo += "\n" + six.ensure_str(sundtek_devices[i]['device'][2:])

			self["tunertwo"] = Label(tunertwo)

		else:
			self["tunerone"] = Label(_("No stick found"))

		self["actions"] = ActionMap(["MenuActions", "OkCancelActions", "ChannelSelectBaseActions", "ColorActions", "ChannelSelectEPGActions"],
		{
			"menu": self.menu,
			"ok": self.save,
			"cancel": self.cancel,
			"red": self.cancel,
			"green": self.save2,
			"yellow": self.restartwhat,
			"blue": self.tunerstart,
			"showEPGList": self.dvbinfo,
			"nextBouquet": self.checkdriverversion,
			"prevBouquet": self.scannetwork,
		}, -2)
		self.onLayoutFinish.append(self.layoutFinished)

	########################################################

	def afterNetworkTest(self, net=True):
		### search for sundtekcontrolcenter updates
		try:
			version = urlopen('http://sundtek.de/media/latest.phtml?sccv=1').read()
			version = six.ensure_str(version)
			version = version.replace('sundtekcontrolcenter_', '')
		except:
			version = "n/a"
		if version == sundtekcontrolcenter_version:
			self["updateavail"].setText("")
		elif version == "n/a":
			self["updateavail"].setText("n/a")
		else:
			try:
				current_version = int(sundtekcontrolcenter_version[:8])
				available_version = int(version[:8])
				if available_version > current_version:
					self["updateavail"].setText(_("scc update available"))
			except:
				self["updateavail"].setText(_("scc update available"))
		### search for sundtek driver update
		s = r"(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2}).(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2})"
		pattern = re.compile(s)
		try:
			netdriver = urlopen('http://sundtek.de/media/latest.phtml?scc').read()
			netdriver = six.ensure_str(netdriver)
		except:
			netdriver = "n/a"
		match = pattern.search(netdriver)
		if match:
			netdriver = match.group("year") + match.group("month") + match.group("day") + match.group("hours") + match.group("minutes") + match.group("seconds")
		else:
			netdriver = "n/a"
		s = r"(?P<year>\d{2})-(?P<month>\d{2})-(?P<day>\d{2}) (?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})"
		pattern = re.compile(s)
		if os.path.exists("/opt/bin/mediaclient"):
			installeddriver = os.popen("/opt/bin/mediaclient --build", "r").read()
		else:
			installeddriver = "n/a"
		match = pattern.search(installeddriver)
		if match:
			installeddriver = match.group("year") + match.group("month") + match.group("day") + match.group("hours") + match.group("minutes") + match.group("seconds")
		else:
			installeddriver = "n/a"
		if (netdriver != "n/a") and (installeddriver != "n/a"):
			if int(netdriver) <= int(installeddriver):
				self["driverupdateavail"].setText("")
			else:
				self["driverupdateavail"].setText(_("driver update available"))
		else:
			self["driverupdateavail"].setText("n/a")

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.updateSettingList()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.updateSettingList()

	def setDeviceCB(self, rv):
		cur = self["config"].getCurrent()
		if cur and rv:
			for i in dir(config.plugins.SundtekControlCenter):
				if i[0:8] == "devices_":
					if cur[1] == config.plugins.SundtekControlCenter.__dict__[i]:
						config.plugins.SundtekControlCenter.__dict__[i].value = "%d" % rv[1]

	def save2(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		self.sundtekconfigfile()
		self.readConfig()
		self.updateDefaults()
		if self.setsettings(exit=True):
			self.close(True, self.session)

	def save(self):
		cur = self["config"].getCurrent()
		if cur:
			for i in dir(config.plugins.SundtekControlCenter):
				if i[0:8] == "devices_":
					if cur[1] == config.plugins.SundtekControlCenter.__dict__[i]:
						# no devices attached - so no device selection possible
						if (cur[1].value == None) or (cur[1].value == ""):
							return
						b = int(cur[1].value)
						idx = int(cur[1].value)
						options = []
						for i in sundtek_devices:
							options.append((_("%s" % sundtek_devices[i]['device']), i))
						self.session.openWithCallback(self.setDeviceCB, ChoiceBox, list=options)
						return
			if cur[1] == config.plugins.SundtekControlCenter.networkIp:
				found = 0
				path = config.plugins.SundtekControlCenter.networkIp.value
				if path:
					for i in sundtek_devices:
						networkpath = sundtek_devices[i]['network_path'].replace(":0", "")
						retval = path.replace(":0", "")
						if (networkpath == retval):
							found = 1
							break
				if (found == 0):
					if os.path.exists("/opt/bin/mediaclient"):
						cmd = "/opt/bin/mediaclient --mount %s" % config.plugins.SundtekControlCenter.networkIp.value
					else:
						return
					os.system(cmd)
					self.session.open(MessageBox, _("Trying to connect to %s (push ok to continue)") % config.plugins.SundtekControlCenter.networkIp.value, MessageBox.TYPE_INFO, 7)
				else:
					self.session.open(MessageBox, _("%s is already connected") % config.plugins.SundtekControlCenter.networkIp.value, MessageBox.TYPE_INFO, 7)
				return

			if cur[1] == config.plugins.SundtekControlCenter.scanNetwork:
				self.scannetwork()
				return

		self.save2()

	def cancel(self):
		for x in self["config"].list:
			x[1].cancel()
		self.close(False, self.session)

	def menu(self):
		options = [
			(_("Install or Update sundtek Driver"), self.checkdriverversion),
			(_("Scan for IPTV server addresses"), self.scannetwork),
			(_("Enable / Disable IP server"), self.enablenetwork),
			(_("Service Mode"), self.enableservicemode),
			(_("Show tuner informations"), self.dvbinfo),
			(_("Backup Drivers to HDD"), self.driverbackup),
			(_("Restore Drivers from HDD"), self.driverrestore),
			(_("Check for a newer version of the SundtekControlCenter"), self.selfupdate),
		]
		if os.path.exists("/etc/sundtek.conf"):
			options.append((_("Show /etc/sundtek.conf"), self.configinfo))
		currentfile = "/usr/script/DVB_C_Tuner_starten.sh"
		if os.path.exists(currentfile):
			fix_vtuner = False
			try:
				f = open(currentfile).readlines()
				for line in f:
					if "[ ! -e /tmp/.sundtekholdstart ] && touch /tmp/.sundtekholdstart && sleep 5 && /usr/sundtek/sun_dvb.sh start_c" in line:
						fix_vtuner = True
			except:
				fix_vtuner = None
			if fix_vtuner:
				options.append((_("Disable tuners type fix"), self.resetfixtunerstype))
		self.session.openWithCallback(self.thismenuCallback, ChoiceBox, list=options)

	def configinfo(self):
		self.prompt("cat /etc/sundtek.conf")

	def thismenuCallback(self, ret):
		ret and ret[1]()

	def resetfixtunerstype(self):
		os.system("echo '#!/bin/sh\nsource /usr/script/DriverCheck.sh\n/usr/sundtek/sun_dvb.sh start_c restart $0\n' > /usr/script/DVB_C_Tuner_starten.sh")

	def updateDeviceList(self):
		global sundtek_devices, vtuner_nifs
		global device_choices, device_choices_whitelist
		if os.path.exists("/opt/bin/mediaclient"):
			devices = os.popen("/opt/bin/mediaclient -e").read()
		else:
			return

		if (devices.find("currently not running") > 0):
			return

		networkpath_result = {}
		devpos = devices.find("device ")
		if (devpos > 0):
			network = devices[devpos + 6:].split("device ")
			i = 0
			for i in range(0, len(network)):
				b = 0
				network_path = ""
				s = r"\[NETWORKPATH\]:\n.+PATH: (.*)"
				pattern = re.compile(s)
				serial_result = {}
				while True:
					match = pattern.search(network[i], b)
					if match:
						network_path = (match.group(1))
						b = match.end() + 1
					else:
						break
				networkpath_result[i] = network_path

		i = 0
		d = 0

		s = r"\[SERIAL\]:\n.+ID: (\w+)"
		pattern = re.compile(s)
		serial_result = {}
		while True:
			match = pattern.search(devices, i)
			if match:
				serial_result[d] = (match.group(1))
				i = match.end() + 1
				d = d + 1
			else:
				break

		s = r"device \d{1,}: \[(.*)\]"
		pattern = re.compile(s)
		i = 0
		d = 0
		device_result = {}
		while True:
			match = pattern.search(devices, i)
			if match:
				device_result[d] = (match.group(1))
				i = match.end() + 1
				d = d + 1
			else:
				break

		s = r"device \d{1,}: (.*)"
		pattern = re.compile(s)

		i = 0
		d = 0
		cap_result = {}
		net_result = {}

		while True:
			match = pattern.search(devices, i)
			if match:
				net_result[d] = False
				cap = []
				line = (match.group(1))
				st = line.find("]  ")
				if (st >= 0):
					s = line[line.find("]  ") + 3:]
					cap_array = s.split(", ")
					# we only support DVB from it
					c = 0
					for b in cap_array:
						if (b[0:3] == "DVB") or (b[0:4] == "ATSC"):
							cap.append(('%d' % c, b))
							c = c + 1
						if (b[0:3] == "NET"):
							net_result[d] = True
				cap_result[d] = cap
				i = match.end() + 1
				d = d + 1
			else:
				break

		device_choices = []
		for i in range(0, d):
			sundtek_devices[i] = {}
			sundtek_devices[i]['device'] = str(i) + " " + device_result[i]
			sundtek_devices[i]['serial'] = serial_result[i]
			sundtek_devices[i]['network_path'] = networkpath_result[i]
			sundtek_devices[i]['network_device'] = net_result[i]
			sundtek_devices[i]['capabilities'] = cap_result[i]
			device_choices.append(('%d' % i, "%d %s" % (i + 1, device_result[i][0:23])))

		device_choices_whitelist = device_choices
		for i in range(0, vtuner_nifs):
			if (len(device_choices) > 0) and len(device_choices) > i:
				config.plugins.SundtekControlCenter.__dict__["devices_%d" % i] = ConfigSelection(default='%d' % i, choices=device_choices)
			else:
				config.plugins.SundtekControlCenter.__dict__["devices_%d" % i] = ConfigNothing()

			if (len(device_choices) > i) and len(device_choices) > 0:
				config.plugins.SundtekControlCenter.__dict__["dvbtransmission1_%d" % i] = ConfigSelection(choices=cap_result[i])
			else:
				config.plugins.SundtekControlCenter.__dict__["dvbtransmission1_%d" % i] = ConfigNothing()
			if (len(net_result) > 0) and len(device_choices) > i:
				config.plugins.SundtekControlCenter.__dict__["network_device_%d" % i] = ConfigYesNo(default=net_result[i])
			else:
				config.plugins.SundtekControlCenter.__dict__["network_device_%d" % i] = ConfigNothing()

	def whitelist(self, item):
		global device_choices_whitelist, device_choices_blacklist, device_choices
		device_choices_whitelist.append(item)
		if item in device_choices_blacklist:
			device_choices_blacklist.remove(item)

	def blacklist(self, item):
		global device_choices_whitelist, device_choices_blacklist
		device_choices_blacklist.append(item)
		if item in device_choices_whitelist:
			device_choices_whitelist.remove(item)

	def updateSettingList(self):
		global orginal_dmm, vtuner_nifs
		optionlist = [] ### creating optionlist
		optionlist.append(getConfigListEntry(_("* Configuration support"), config.plugins.SundtekControlCenter.sunconf.support))
		if config.plugins.SundtekControlCenter.sunconf.support.value == "1":
			sublist = [
				getConfigListEntry(_("      Autostart"), config.plugins.SundtekControlCenter.sunconf.autostart),
				getConfigListEntry(_("      Driver autoupdate"), config.plugins.SundtekControlCenter.sunconf.autoupdate),
				getConfigListEntry(_("      Loglevel"), config.plugins.SundtekControlCenter.sunconf.loglevel),
				getConfigListEntry(_("      Enable TV Server"), config.plugins.SundtekControlCenter.sunconf.networkmode),
				getConfigListEntry(_("      Hardware PID Filter"), config.plugins.SundtekControlCenter.sunconf.dmhwpidfilter),
				getConfigListEntry(_("      vTuner acceleration for DM800"), config.plugins.SundtekControlCenter.sunconf.vtuneracceleration),
			]
			optionlist.extend(sublist)

		for i in range(0, vtuner_nifs):
			optionlist.append(getConfigListEntry(_("Enable Tuner %d") % int(i + 1), config.plugins.SundtekControlCenter.__dict__["tuner_enabled_%d" % i]))
			if config.plugins.SundtekControlCenter.__dict__["tuner_enabled_%d" % i].value:
				optionlist.append(getConfigListEntry(_("* Device"), config.plugins.SundtekControlCenter.__dict__["devices_%d" % i]))
				optionlist.append(getConfigListEntry(_("* DVB Mode"), config.plugins.SundtekControlCenter.__dict__["dvbtransmission1_%d" % i]))
		optionlist.append(getConfigListEntry(_("Scan and connect to a TV Server"), config.plugins.SundtekControlCenter.scanNetwork))
		optionlist.append(getConfigListEntry(_("Connect to TV Server IP"), config.plugins.SundtekControlCenter.networkIp))
		if not orginal_dmm:
			optionlist.append(getConfigListEntry(_("Auto checking new version driver/plugin"), config.plugins.SundtekControlCenter.sunconf.searchversion))
		optionlist.append(getConfigListEntry(_("Add show plugin"), config.plugins.SundtekControlCenter.display))
		self["config"].list = optionlist
		self["config"].l.setList(optionlist)

	def layoutFinished(self):
		self.setTitle(_("Sundtek Control Center"))
		if config.plugins.SundtekControlCenter.sunconf.searchversion.value:
			self.startTestNetwork()
		else:
			self.network = True

	def startTestNetwork(self):
		self.testThread = Thread(target=self.start_test)
		self.testThread.start()

	def get_iface_list(self):
		names = array.array('B', '\0' * BYTES)
		sck = socket(AF_INET, SOCK_DGRAM)
		bytelen = struct.unpack('iL', fcntl.ioctl(sck.fileno(), SIOCGIFCONF, struct.pack('iL', BYTES, names.buffer_info()[0])))[0]
		sck.close()
		namestr = names.tostring()
		return [namestr[i:i + 32].split('\0', 1)[0] for i in range(0, bytelen, 32)]

	def start_test(self):
		global testOK
		link = "down"
		for iface in self.get_iface_list():
			if "lo" in iface:
				continue
			if os.path.exists("/sys/class/net/%s/operstate" % (iface)):
				fd = open("/sys/class/net/%s/operstate" % (iface), "r")
				link = fd.read().strip()
				fd.close()
			if link != "down":
				break
		if link != "down":
			s = socket(AF_INET, SOCK_STREAM)
			s.settimeout(2.0)
			try:
				testOK = not bool(s.connect_ex(("www.sundtek.de", 80)))
			except:
				testOK = None
			if not testOK:
				self["updateavail"].setText(_("www.sundtek.de unavailable"))
			else:
				s.shutdown(SHUT_RDWR)
				self.network = True
				self.afterNetworkTest()
			s.close()
		else:
			self["updateavail"].setText(_("Not found network connection"))

	#### scc update
	def selfupdate(self):
		if not self.network:
			return
		try:
			self.version = urlopen('http://sundtek.de/media/latest.phtml?sccv=1').read()
			self.version = six.ensure_str(self.version)
			self.version = self.version.replace('sundtekcontrolcenter_', '')
		except:
			self.version = "n/a"
		if self.version == sundtekcontrolcenter_version:
			self.session.open(MessageBox, _("Latest version is already installed"), MessageBox.TYPE_INFO, 7)
		elif self.version == "n/a":
			self.session.open(MessageBox, _("Check not possible. Please ensure that the Box is connected to the internet."), MessageBox.TYPE_INFO, 7)
		else:
			update = False
			try:
				current_version = int(sundtekcontrolcenter_version[:8])
				available_version = int(self.version[:8])
				if available_version > current_version:
					update = True
				else:
					self.session.open(MessageBox, _("Latest version is already installed"), MessageBox.TYPE_INFO, 7)
			except:
				update = True
			if update:
				self.session.open(MessageBox, _("A newer version of the sundtekcontrolcenter plugin is available.\nif you read this message, please notify the OpenEight Team at:\nhttps://octagon-forum.eu\nto update this embedded version."), MessageBox.TYPE_INFO, 10)


	#### check sundtek driverversion
	def checkdriverversion(self):
		if not self.network:
			return
		s = r"(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2}).(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2})"
		pattern = re.compile(s)
		text = _("Build date :")
		try:
			netdriver = urlopen('http://sundtek.de/media/latest.phtml?scc').read()
			netdriver = six.ensure_str(netdriver)
		except:
			netdriver = text + "n/a"
		match = pattern.search(netdriver)
		if match:
			match = match.group("year") + " " + match.group("month") + " " + match.group("day") + " " + match.group("hours") + " " + match.group("minutes") + " " + match.group("seconds")
			sundtekdriverdate = time.strptime(match, "%y %m %d %H %M %S")
			netdriver = text + time.strftime("%Y-%m-%d %H:%M:%S", sundtekdriverdate)
		else:
			netdriver = text + "n/a"
		if os.path.exists("/opt/bin/mediaclient"):
			installeddriver = os.popen("/opt/bin/mediaclient --build", "r").read()
			if installeddriver.startswith("Build date:"):
				try:
					installeddriver = text + installeddriver[11:]
				except:
					pass
		else:
			installeddriver = text + "n/a"
		self.session.openWithCallback(self.disclaimer, MessageBox, _("latest sundtek driver version:\n") + netdriver + "\n" + _("\nyour driver version:\n") + installeddriver + _("\nUpdate to current sundtek driver version?"), MessageBox.TYPE_YESNO)

	def disclaimer(self, result):
		if result:
			os.popen("chmod 755 /usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/sundtekinstall.sh > /dev/null 2>&1")
			self.prompt("/usr/lib/enigma2/python/Plugins/Extensions/ExtrasPanel/sundtekinstall.sh")

	#### search for ip servers
	def parseforip(self):
		if os.path.exists("/opt/bin/mediaclient"):
			lines = os.popen("/opt/bin/mediaclient --scan-network").readlines()
		else:
			return []
		sticks = []
		if len(lines) == 6:
			sticks = [0]
		elif len(lines) >= 7:
			sticks = [0, 0]
		if len(sticks) == 1:
			sticks[0] = lines[4].split("|")
			sticks[0] = sticks[0][0].strip() + ":" + sticks[0][1].strip()
		elif len(sticks) >= 2:
			sticks[0] = lines[4].split("|")
			sticks[1] = lines[5].split("|")
			sticks[0] = sticks[0][0].strip() + ":" + sticks[0][1].strip()
			sticks[1] = sticks[1][0].strip() + ":" + sticks[1][1].strip()
			try:
				sticks[2] = lines[6].split("|")
				sticks[2] = sticks[2][0].strip() + ":" + sticks[2][1].strip()
			except:
				pass
		else:
			### no info found
			sticks = []
		return sticks

	def iptvServers(self, ret):
		found = 0
		if ret:
			for i in sundtek_devices:
				networkpath = sundtek_devices[i]['network_path'].replace(":0", "")
				retval = ret[0].replace(":0", "")
				if (networkpath == retval):
					found = 1
					break
		if (found == 0) and ret:
			if os.path.exists("/opt/bin/mediaclient"):
				cmd = "/opt/bin/mediaclient --mount %s" % ret[0]
				r = os.system(cmd)
		self.updateDeviceList()
		self.readConfig()
		self.updateDefaults()
		self.updateSettingList()
		return

	def scannetwork(self):
		selected = 0
		if os.path.exists("/opt/bin/mediaclient"):
			iplist = self.parseforip()
			if len(iplist) >= 1:
				options = []
				for i in iplist:
					options.append((i, selected))
				self.session.openWithCallback(self.iptvServers, ChoiceBox, list=options)
			else:
				self.session.open(MessageBox, _("No IPTV media server found"), MessageBox.TYPE_INFO, 7)

	def enablenetwork(self):
		if not os.path.exists("/opt/bin/mediaclient"):
			return
		options = [(_("Enable the IP server"), self.startipserver), (_("Disable the IP server"), self.stopipserver)]
		self.session.openWithCallback(self.thismenuCallback, ChoiceBox, list=options)

	def startipserver(self):
		os.popen("/opt/bin/mediaclient --enablenetwork=on")
		self.session.open(MessageBox, _("IP server is enabled"), MessageBox.TYPE_INFO)

	def stopipserver(self):
		os.popen("/opt/bin/mediaclient --enablenetwork=off")
		self.session.open(MessageBox, _("IP server is disabled"), MessageBox.TYPE_INFO)

	def enableservicemode(self):
		if not os.path.exists("/opt/bin/mediaclient"):
			return
		self.session.openWithCallback(self.startservicemode, MessageBox, _("Service Mode starts a tunnel to the sundtek server. Please start service mode only if requested by sundtek support.\n\nStart Service Mode now?"), MessageBox.TYPE_YESNO)

	def startservicemode(self, result):
		if result:
			os.popen("/opt/bin/mediaclient --portforward 23")
			self.prompt("/opt/bin/mediaclient --portforward 23")

	def driverbackup(self):
		try:
			mounts = open("/proc/mounts")
		except:
			return
		hdd = False
		mountcheck = mounts.readlines()
		mounts.close()
		for line in mountcheck:
			if '/media/hdd' in line:
				hdd = True
				break
		if not hdd:
			self.session.open(MessageBox, _("Not found folder '/media/hdd'."), MessageBox.TYPE_INFO, 5)
			return
		backuppath = "/media/hdd/backup/SundtekBackup"
		now = datetime.datetime.now()
		backupfile = "sundtek-" + now.strftime("%Y%m%d-%H%M") + ".tar"
		if not os.path.exists(backuppath): # backup folder does not yet exist
			os.makedirs(backuppath)
		self.prompt("echo 'Wait...create backup\n' && tar -czvf" + " " + backuppath + "/" + backupfile + " /usr/sundtek /opt/bin /etc/sundtek.conf /etc/sundtek.net > /dev/null 2>&1")

	def driverrestore(self):
		restorepath = "/media/hdd/backup/SundtekBackup"
		if (os.path.exists(restorepath)): # backup folder exists
			backupfile = [line.rstrip('\n') for line in (os.popen("ls " + restorepath + "/sundtek*tar").readlines())]
			if len(backupfile) > 0: # found at least one backup in the backupfolder
				options = []
				restorelist = []
				restorelist = [item.lstrip(restorepath) for item in backupfile]
				for item in backupfile:
					options.append((_(restorelist.pop()), None))
				self.session.openWithCallback(self.restoremenuCallback, ChoiceBox, list=options)
			else: # there is no backup file found
				self.session.open(MessageBox, _("No backup file was found."), MessageBox.TYPE_INFO, 10)
		else:
			self.session.open(MessageBox, _("No backups found."), MessageBox.TYPE_INFO, 10)

	def restoremenuCallback(self, ret):
		if ret:
			restore = ("tar -xvpzf /media/hdd/backup/SundtekBackup/%s -C /") % str(ret[0])
			self.prompt(restore) # restore from root
			self.session.open(MessageBox, _("Restoreing:  %s") % str(ret[0]), MessageBox.TYPE_INFO, 7)
		else:
			self.session.open(MessageBox, _("Restore was canceled"), MessageBox.TYPE_INFO, 7)

	def restartwhat(self):
		if self.session.nav.getRecordings():
			self.session.open(MessageBox, _("Warning! Recording is currently running."), MessageBox.TYPE_INFO)
			return
		options = [
			(_("Restart E2"), self.restartenigma),
			(_("Reboot box"), self.restartingbox),
		]
		self.session.openWithCallback(self.thismenuCallback, ChoiceBox, list=options)

	def restartenigma(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		self.sundtekconfigfile()
		self.setsettings()
		self.session.open(TryQuitMainloop, 3)

	def restartingbox(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		self.sundtekconfigfile()
		self.setsettings()
		self.session.open(TryQuitMainloop, 2)

	def dvbinfo(self):
		if os.path.exists("/usr/sundtek/sun_dvb.sh"):
			self.prompt("/usr/sundtek/sun_dvb.sh info")

	def installdriverrequest(self, result):
		if result:
			self.session.openWithCallback(self.disclaimer, MessageBox, _("Sundtek legal notice:\nThis software comes without any warranty, use it at your own risk?\nContinue?"), MessageBox.TYPE_YESNO)

	def prompt(self, com):
		self.session.open(Console, (""), ["%s" % com])

####################################################################

#### config file section
	def parsefornetworkstickserial(self):
		lines = os.popen("/opt/bin/mediaclient --scan-network").readlines()

		sticks = []
		if len(lines) == 6:
			sticks = [0]
		elif len(lines) >= 7:
			sticks = [0, 0]

		if len(sticks) == 1:
			sticks[0] = lines[4].split("|")
			sticks[0] = sticks[0][5].strip()
		elif len(sticks) >= 2:
			sticks[0] = lines[4].split("|")
			sticks[1] = lines[5].split("|")

			sticks[0] = sticks[0][5].strip()
			sticks[1] = sticks[1][5].strip()
		else:
			### no info found
			sticks = []

		return sticks

	def sundtekconfigfile(self):
		global vtuner_nifs, sundtek_devices
		if (len(sundtek_devices) == 0):
			return
		conffile = "/etc/sundtek.conf"
		now = datetime.datetime.now()
		results = []
		### no network
		s = r"\[SERIAL\]:\n.+ID: (\w+)"
		pattern = re.compile(s)
		#devices = os.popen("cat /usr/sundtek/test.txt").read()
		devices = os.popen("/opt/bin/mediaclient -e").read()
		i = 0
		while True:
			match = pattern.search(devices, i)
			if match:
				results.append(match.group(1))
				i = match.end() + 1
			else:
				break
		#### header
		header1 = ("# sundtek configuration file - /etc/sundtek.conf\n")
		header2 = ("# created / modified: " + (now.strftime("%b %d %Y, %H:%Mh")) + " by sundtekcontrolcenter " + sundtekcontrolcenter_version + "\n\n")
		header = header1 + header2

		#### configuration (loglevel, autoupdate, vtuneracceleration, dmhwpidfilter, networkmode)
		loglevel = ""
		autoupdate = ""
		vtuneracceleration = ""
		dmhwpidfilter = ""
		networkmode = ""
		loglevel = str(config.plugins.SundtekControlCenter.sunconf.loglevel.value) # loglevel
		if (loglevel == "1"):
			os.system("/opt/bin/mediaclient --loglevel=min")
			loglevel = "loglevel = min\n"
		elif (loglevel == "2"):
			os.system("/opt/bin/mediaclient --loglevel=max")
			loglevel = "loglevel = max\n"
		else:
			os.system("/opt/bin/mediaclient --loglevel=off")
			loglevel = "loglevel = off\n"

		autoupdate = str(config.plugins.SundtekControlCenter.sunconf.autoupdate.value) # driver autoupdate
		if (autoupdate == "True"):
			autoupdate = "autoupdate = on\n"
		else:
			autoupdate = "autoupdate = off\n"
		dmhwpidfilter = str(config.plugins.SundtekControlCenter.sunconf.dmhwpidfilter.value) # dmhwpidfilter autoupdate
		if (dmhwpidfilter == "1"):
			dmhwpidfilter = "dmhwpidfilter = on\n"
		else:
			dmhwpidfilter = "dmhwpidfilter = off\n"
		vtuneracceleration = str(config.plugins.SundtekControlCenter.sunconf.vtuneracceleration.value) # vtuner acceleration
		if (vtuneracceleration == "True"):
			vtuneracceleration = "vtuner_acceleration = on\n"
		else:
			vtuneracceleration = "vtuner_acceleration = off\n"
		networkmode = str(config.plugins.SundtekControlCenter.sunconf.networkmode.value) #networkmode
		if (networkmode == "1"):
			networkmode = "enablenetwork = on\n"
		else:
			networkmode = "enablenetwork = off\n"

		#### sticks
		netsection = ""
		for i in range(0, len(sundtek_devices)):
			if netsection == "" and len(sundtek_devices[i]['network_path']) > 0:
				netsection = "[NETWORK]\n"
			if (len(sundtek_devices[i]['network_path']) > 0):
				netsection += "device=" + sundtek_devices[i]['network_path'] + "\n"
		show_message = False

		#stick 1 data
		tunerconf = ""
		devlist = []
		for i in range(0, vtuner_nifs):
			if config.plugins.SundtekControlCenter.__dict__["tuner_enabled_%d" % i].value:
				# quick protection which makes it impossible to register an input twice
				if (config.plugins.SundtekControlCenter.__dict__["devices_%d" % i].value != ""):
					deviceid = int(config.plugins.SundtekControlCenter.__dict__["devices_%d" % i].value)
					if deviceid not in devlist:
						devlist.append(deviceid)
						tunerconf += "###### configuration stick %d\n" % i

						serial = sundtek_devices[deviceid]['serial']
						current_description = config.plugins.SundtekControlCenter.__dict__["devices_%d" % i].getText()
						if current_description and _("Dual") in current_description:
							tunerconf += ("[" + serial + "/1]\n")
							tunerconf += "dreambox_support_fe1=on\n\n"
						tunerconf += ("[" + serial + "]\n")
						if len(sundtek_devices[deviceid]['network_path']):
							tunerconf += "netrecoverymode=on\n"
						dvbtransmission = str(config.plugins.SundtekControlCenter.__dict__["dvbtransmission1_%d" % i].value)
						try:
							mode = int(config.plugins.SundtekControlCenter.__dict__['dvbtransmission1_%d' % i].value)
							mode = str(sundtek_devices[deviceid]['capabilities'][mode][1])
							mode = mode.replace("-", "")
						except:
							mode = ""
						if mode:
							tunerconf += "initial_dvb_mode=" + mode + "\n"
							tunerconf += "dreambox_support_fe1=on\n\n"
						else:
							tunerconf = ""

		data = header + loglevel + autoupdate + dmhwpidfilter + vtuneracceleration + networkmode + "\n" + netsection + tunerconf
		### (over)write file
		f = open(conffile, "w")
		f.writelines(data)
		f.close()

####################################################################

#### settings
	def setsettings(self, exit=False, use_os=False):
		### check if driver is installed
		if ((not os.path.exists("/opt/bin/mediasrv")) or (not os.path.exists("/opt/bin/mediaclient")) or (not os.path.exists("/usr/sundtek/sun_dvb.sh"))):
			## maybe driver not installed
			if (os.path.exists("/usr/sundtek/mediasrv") and os.path.exists("/usr/sundtek/mediaclient") and os.path.exists("/usr/sundtek/sun_dvb.sh")) and os.path.exists("/usr/sundtek/libmediaclient.so"):
				## driver installed but no links in /opt/bin
				if (not os.path.exists("/opt/bin")):
					os.makedirs("/opt/bin")
				if (not os.path.exists("/opt/lib")):
					os.makedirs("/opt/lib")
				os.popen("ln -s /usr/sundtek/mediasrv /opt/bin/mediasrv")
				os.popen("ln -s /usr/sundtek/mediaclient /opt/bin/mediaclient")
				os.popen("ln -s /usr/sundtek/libmediaclient.so /opt/lib/libmediaclient.so")
			else:
				## driver not installed
				self.session.openWithCallback(self.installdriverrequest, MessageBox, _("It seems the sundtek driver is not installed or not installed properly. Install the driver now?"), MessageBox.TYPE_YESNO)
				if exit:
					return False
		else:
			### driver installed
			### disable autostart
			if config.plugins.SundtekControlCenter.sunconf.autostart.value == False:
				cmd = "/usr/sundtek/sun_dvb.sh noautostart"
				if use_os:
					os.system(cmd)
				else:
					self.prompt(cmd)
			else:
				# as soon as the configuration file is written the driver will make use of the configuration file
				# and ignore the command line configuration
				if config.plugins.SundtekControlCenter.sunconf.autostart.value == True:
					### enable autostart
					cmd = "/usr/sundtek/sun_dvb.sh autostart_c"
					if use_os:
						os.system(cmd)
					else:
						self.prompt(cmd)
		return True

	def tunerstart(self):
		for x in self["config"].list:
			x[1].save()
		configfile.save()
		self.sundtekconfigfile()
		self.setsettings(use_os=True)
		if self.session.nav.getRecordings():
			self.session.open(MessageBox, _("Warning! Recording is currently running."), MessageBox.TYPE_INFO)
			return
		else:
			self.session.nav.stopService()
		if (os.path.exists("/opt/bin/mediasrv")) and (os.path.exists("/opt/bin/mediaclient")) and (os.path.exists("/usr/sundtek/sun_dvb.sh")):
			try:
				from enigma import eEPGCache
				epgcache = eEPGCache.getInstance()
				epgcache.save()
			except:
				pass
			self.prompt("echo 'Wait...' && sleep 8 && /usr/sundtek/sun_dvb.sh start_c restart")
