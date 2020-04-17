from boxbranding import getBoxType

from twisted.internet import threads
from enigma import eDBoxLCD, eTimer

from config import config, ConfigSubsection, ConfigSelection, ConfigSlider, ConfigYesNo, ConfigNothing
from Components.SystemInfo import SystemInfo
from Tools.Directories import fileExists
import usb

def IconCheck(session=None, **kwargs):
	if fileExists("/proc/stb/lcd/symbol_network") or fileExists("/proc/stb/lcd/symbol_usb"):
		global networklinkpoller
		networklinkpoller = IconCheckPoller()
		networklinkpoller.start()

class IconCheckPoller:
	def __init__(self):
		self.timer = eTimer()

	def start(self):
		if self.iconcheck not in self.timer.callback:
			self.timer.callback.append(self.iconcheck)
		self.timer.startLongTimer(0)

	def stop(self):
		if self.iconcheck in self.timer.callback:
			self.timer.callback.remove(self.iconcheck)
		self.timer.stop()

	def iconcheck(self):
		threads.deferToThread(self.JobTask)
		self.timer.startLongTimer(30)

	def JobTask(self):
		LinkState = 0
		if fileExists('/sys/class/net/wlan0/operstate'):
			LinkState = open('/sys/class/net/wlan0/operstate').read()
			if LinkState != 'down':
				LinkState = open('/sys/class/net/wlan0/operstate').read()
		elif fileExists('/sys/class/net/eth0/operstate'):
			LinkState = open('/sys/class/net/eth0/operstate').read()
			if LinkState != 'down':
				LinkState = open('/sys/class/net/eth0/carrier').read()
		LinkState = LinkState[:1]
		if fileExists("/proc/stb/lcd/symbol_network") and config.lcd.mode.value == '1':
			f = open("/proc/stb/lcd/symbol_network", "w")
			f.write(str(LinkState))
			f.close()
		elif fileExists("/proc/stb/lcd/symbol_network") and config.lcd.mode.value == '0':
			f = open("/proc/stb/lcd/symbol_network", "w")
			f.write('0')
			f.close()

		USBState = 0
		busses = usb.busses()
		for bus in busses:
			devices = bus.devices
			for dev in devices:
				if dev.deviceClass != 9 and dev.deviceClass != 2 and dev.idVendor > 0:
					USBState = 1
		if fileExists("/proc/stb/lcd/symbol_usb") and config.lcd.mode.value == '1':
			f = open("/proc/stb/lcd/symbol_usb", "w")
			f.write(str(USBState))
			f.close()
		elif fileExists("/proc/stb/lcd/symbol_usb") and config.lcd.mode.value == '0':
			f = open("/proc/stb/lcd/symbol_usb", "w")
			f.write('0')
			f.close()

		self.timer.startLongTimer(30)

class LCD:
	def __init__(self):
		pass

	def setBright(self, value):
		value *= 255
		value /= 10
		if value > 255:
			value = 255
		eDBoxLCD.getInstance().setLCDBrightness(value)

	def setContrast(self, value):
		value *= 63
		value /= 20
		if value > 63:
			value = 63
		eDBoxLCD.getInstance().setLCDContrast(value)

	def setInverted(self, value):
		if value:
			value = 255
		eDBoxLCD.getInstance().setInverted(value)

	def setFlipped(self, value):
		eDBoxLCD.getInstance().setFlipped(value)

	def isOled(self):
		return eDBoxLCD.getInstance().isOled()

	def setMode(self, value):
		print 'setLCDMode',value
		f = open("/proc/stb/lcd/show_symbols", "w")
		f.write(value)
		f.close()

	def setPower(self, value):
		print 'setLCDPower',value
		f = open("/proc/stb/power/vfd", "w")
		f.write(value)
		f.close()

	def setEt8500(self, value):
		print 'setLCDet8500',value
		f = open("/proc/stb/fb/sd_detach", "w")
		f.write(value)
		f.close()

	def setRepeat(self, value):
		print 'setLCDRepeat',value
		f = open("/proc/stb/lcd/scroll_repeats", "w")
		f.write(value)
		f.close()

	def setScrollspeed(self, value):
		print 'setLCDScrollspeed',value
		f = open("/proc/stb/lcd/scroll_delay", "w")
		f.write(str(value))
		f.close()

	def setLEDNormalState(self, value):
		eDBoxLCD.getInstance().setLED(value, 0)

	def setLEDDeepStandbyState(self, value):
		eDBoxLCD.getInstance().setLED(value, 1)

	def setLEDBlinkingTime(self, value):
		eDBoxLCD.getInstance().setLED(value, 2)

def leaveStandby():
	config.lcd.bright.apply()
	config.lcd.ledbrightness.apply()
	config.lcd.ledbrightnessdeepstandby.apply()

def standbyCounterChanged(dummy):
	from Screens.Standby import inStandby
	inStandby.onClose.append(leaveStandby)
	config.lcd.standby.apply()
	config.lcd.ledbrightnessstandby.apply()
	config.lcd.ledbrightnessdeepstandby.apply()

def InitLcd():
	detected = eDBoxLCD.getInstance() and eDBoxLCD.getInstance().detected()
	config.lcd = ConfigSubsection();
	if detected:
		config.lcd.scroll_speed = ConfigSelection(default = "300", choices = [
			("500", _("slow")),
			("300", _("normal")),
			("100", _("fast"))])
		config.lcd.scroll_delay = ConfigSelection(default = "10000", choices = [
			("10000", "10 " + _("seconds")),
			("20000", "20 " + _("seconds")),
			("30000", "30 " + _("seconds")),
			("60000", "1 " + _("minute")),
			("300000", "5 " + _("minutes")),
			("noscrolling", _("off"))])
	
		def setLCDbright(configElement):
			ilcd.setBright(configElement.value)

		def setLCDcontrast(configElement):
			ilcd.setContrast(configElement.value)

		def setLCDinverted(configElement):
			ilcd.setInverted(configElement.value)

		def setLCDflipped(configElement):
			ilcd.setFlipped(configElement.value)

		def setLCDmode(configElement):
			ilcd.setMode(configElement.value)

		def setLCDpower(configElement):
			ilcd.setPower(configElement.value);
			
		def setLCD8500(configElement):
			ilcd.setEt8500(configElement.value);

		def setLCDrepeat(configElement):
			ilcd.setRepeat(configElement.value)

		def setLCDscrollspeed(configElement):
			ilcd.setScrollspeed(configElement.value)

		def setLEDnormalstate(configElement):
			ilcd.setLEDNormalState(configElement.value)

		def setLEDdeepstandby(configElement):
			ilcd.setLEDDeepStandbyState(configElement.value)

		def setLEDblinkingtime(configElement):
			ilcd.setLEDBlinkingTime(configElement.value)

		def setLedPowerColor(configElement):
			f = open("/proc/stb/fp/ledpowercolor", "w")
			f.write(configElement.value)
			f.close()

		def setLedStandbyColor(configElement):
			f = open("/proc/stb/fp/ledstandbycolor", "w")
			f.write(configElement.value)
			f.close()

		def setLedSuspendColor(configElement):
			f = open("/proc/stb/fp/ledsuspendledcolor", "w")
			f.write(configElement.value)
			f.close()

		def setPower4x7On(configElement):
			f = open("/proc/stb/fp/power4x7on", "w")
			f.write(configElement.value)
			f.close()

		def setPower4x7Standby(configElement):
			f = open("/proc/stb/fp/power4x7standby", "w")
			f.write(configElement.value)
			f.close()

		def setPower4x7Suspend(configElement):
			f = open("/proc/stb/fp/power4x7suspend", "w")
			f.write(configElement.value)
			f.close()

		standby_default = 5

		ilcd = LCD()

		if not ilcd.isOled():
			config.lcd.contrast = ConfigSlider(default=5, limits=(0, 20))
			config.lcd.contrast.addNotifier(setLCDcontrast)
		else:
			config.lcd.contrast = ConfigNothing()
			standby_default = 1

		config.lcd.standby = ConfigSlider(default=standby_default, limits=(0, 10))
		config.lcd.standby.addNotifier(setLCDbright)
		config.lcd.standby.apply = lambda : setLCDbright(config.lcd.standby)

		config.lcd.bright = ConfigSlider(default=5, limits=(0, 10))
		config.lcd.bright.addNotifier(setLCDbright)
		config.lcd.bright.apply = lambda : setLCDbright(config.lcd.bright)
		config.lcd.bright.callNotifiersOnSaveAndCancel = True

		config.lcd.invert = ConfigYesNo(default=False)
		config.lcd.invert.addNotifier(setLCDinverted)

		config.lcd.flip = ConfigYesNo(default=False)
		config.lcd.flip.addNotifier(setLCDflipped)

		if fileExists("/proc/stb/fp/ledpowercolor"):
			config.lcd.ledpowercolor = ConfigSelection(default = "1", choices = [("0", _("off")),("1", _("blue")), ("2", _("red")), ("3", _("violet"))])
			config.lcd.ledpowercolor.addNotifier(setLedPowerColor)

		if fileExists("/proc/stb/fp/ledstandbycolor"):
			config.lcd.ledstandbycolor = ConfigSelection(default = "3", choices = [("0", _("off")),("1", _("blue")), ("2", _("red")), ("3", _("violet"))])
			config.lcd.ledstandbycolor.addNotifier(setLedStandbyColor)

		if fileExists("/proc/stb/fp/ledsuspendledcolor"):
			config.lcd.ledsuspendcolor = ConfigSelection(default = "2", choices = [("0", _("off")),("1", _("blue")), ("2", _("red")), ("3", _("violet"))])
			config.lcd.ledsuspendcolor.addNotifier(setLedSuspendColor)

		if fileExists("/proc/stb/fp/power4x7on"):
			config.lcd.power4x7on = ConfigSelection(default = "on", choices = [("off", _("Off")), ("on", _("On"))])
			config.lcd.power4x7on.addNotifier(setPower4x7On)

		if fileExists("/proc/stb/fp/power4x7standby"):
			config.lcd.power4x7standby = ConfigSelection(default = "on", choices = [("off", _("Off")), ("on", _("On"))])
			config.lcd.power4x7standby.addNotifier(setPower4x7Standby)

		if fileExists("/proc/stb/fp/power4x7suspend"):
			config.lcd.power4x7suspend = ConfigSelection(default = "on", choices = [("off", _("Off")), ("on", _("On"))])
			config.lcd.power4x7suspend.addNotifier(setPower4x7Suspend)

		if fileExists("/proc/stb/lcd/scroll_delay"):
			config.lcd.scrollspeed = ConfigSlider(default = 150, increment = 10, limits = (0, 500))
			config.lcd.scrollspeed.addNotifier(setLCDscrollspeed)
			config.lcd.repeat = ConfigSelection([("0", _("None")), ("1", _("1X")), ("2", _("2X")), ("3", _("3X")), ("4", _("4X")), ("500", _("Continues"))], "3")
			config.lcd.repeat.addNotifier(setLCDrepeat)
			config.lcd.mode = ConfigSelection([("0", _("No")), ("1", _("Yes"))], "1")
			config.lcd.mode.addNotifier(setLCDmode)
		else:
			config.lcd.mode = ConfigNothing()
			config.lcd.repeat = ConfigNothing()
			config.lcd.scrollspeed = ConfigNothing()

		if fileExists("/proc/stb/power/vfd"):
			config.lcd.power = ConfigSelection([("0", _("Off")), ("1", _("On"))], "1")
			config.lcd.power.addNotifier(setLCDpower);
		else:
			config.lcd.power = ConfigNothing()
			
		if fileExists("/proc/stb/fb/sd_detach"):
			config.lcd.et8500 = ConfigSelection([("1", _("No")), ("0", _("Yes"))], "0")
			config.lcd.et8500.addNotifier(setLCD8500);
		else:
			config.lcd.et8500 = ConfigNothing()

		if getBoxType() == 'vuultimo':
			config.lcd.ledblinkingtime = ConfigSlider(default = 5, increment = 1, limits = (0,15))
			config.lcd.ledblinkingtime.addNotifier(setLEDblinkingtime)
			config.lcd.ledbrightnessdeepstandby = ConfigSlider(default = 1, increment = 1, limits = (0,15))
			config.lcd.ledbrightnessdeepstandby.addNotifier(setLEDnormalstate)
			config.lcd.ledbrightnessdeepstandby.addNotifier(setLEDdeepstandby)
			config.lcd.ledbrightnessdeepstandby.apply = lambda : setLEDdeepstandby(config.lcd.ledbrightnessdeepstandby)
			config.lcd.ledbrightnessstandby = ConfigSlider(default = 1, increment = 1, limits = (0,15))
			config.lcd.ledbrightnessstandby.addNotifier(setLEDnormalstate)
			config.lcd.ledbrightnessstandby.apply = lambda : setLEDnormalstate(config.lcd.ledbrightnessstandby)
			config.lcd.ledbrightness = ConfigSlider(default = 3, increment = 1, limits = (0,15))
			config.lcd.ledbrightness.addNotifier(setLEDnormalstate)
			config.lcd.ledbrightness.apply = lambda : setLEDnormalstate(config.lcd.ledbrightness)
			config.lcd.ledbrightness.callNotifiersOnSaveAndCancel = True
		else:
			def doNothing():
				pass
			config.lcd.ledbrightness = ConfigNothing()
			config.lcd.ledbrightness.apply = lambda : doNothing()
			config.lcd.ledbrightnessstandby = ConfigNothing()
			config.lcd.ledbrightnessstandby.apply = lambda : doNothing()
			config.lcd.ledbrightnessdeepstandby = ConfigNothing()
			config.lcd.ledbrightnessdeepstandby.apply = lambda : doNothing()
			config.lcd.ledblinkingtime = ConfigNothing()
	else:
		def doNothing():
			pass
		config.lcd.contrast = ConfigNothing()
		config.lcd.bright = ConfigNothing()
		config.lcd.standby = ConfigNothing()
		config.lcd.bright.apply = lambda : doNothing()
		config.lcd.standby.apply = lambda : doNothing()
		config.lcd.mode = ConfigNothing()
		config.lcd.power = ConfigNothing()
		config.lcd.et8500 = ConfigNothing()
		config.lcd.repeat = ConfigNothing()
		config.lcd.scrollspeed = ConfigNothing()
		config.lcd.ledbrightness = ConfigNothing()
		config.lcd.ledbrightness.apply = lambda : doNothing()
		config.lcd.ledbrightnessstandby = ConfigNothing()
		config.lcd.ledbrightnessstandby.apply = lambda : doNothing()
		config.lcd.ledbrightnessdeepstandby = ConfigNothing()
		config.lcd.ledbrightnessdeepstandby.apply = lambda : doNothing()
		config.lcd.ledblinkingtime = ConfigNothing()

	config.misc.standbyCounter.addNotifier(standbyCounterChanged, initial_call = False)

def setLCDLiveTv(value):
	if "live_enable" in SystemInfo["LcdLiveTV"]:
		open(SystemInfo["LcdLiveTV"], "w").write(value and "enable" or "disable")
	else:
		open(SystemInfo["LcdLiveTV"], "w").write(value and "0" or "1")
	if not value:
		try:
			InfoBarInstance = InfoBar.instance
			InfoBarInstance and InfoBarInstance.session.open(dummyScreen)
		except:
			pass

def leaveStandbyLCDLiveTV():
	if config.lcd.showTv.value:
		setLCDLiveTv(True)

def standbyCounterChangedLCDLiveTV(dummy):
	if config.lcd.showTv.value:
		from Screens.Standby import inStandby
		if leaveStandbyLCDLiveTV not in inStandby.onClose:
			inStandby.onClose.append(leaveStandbyLCDLiveTV)
		setLCDLiveTv(False)
