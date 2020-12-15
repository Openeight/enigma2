installdir = $(pkgdatadir)/display/skin_default

if HAVE_COLORLCD
dist_install_DATA = skin_display96.xml
else
if ET8500
dist_install_DATA = skin_display.xml
SUBDIRS = LCDAnalogClock_1_Standby LCDAnalogClock_2_Standby LCDWeather_Standby LCDAnalogClock_3_Weather_Infobar
endif
if HAVE_COLORLCD220
SUBDIRS = display220
endif
if ET10000
dist_install_DATA = skin_display.xml
else
DISPLAYTYPE = display
endif
endif

dist_install_DATA = skin_display.xml

# Use box-specific XML if it exists, otherwise get the default
# TEXTSKIN is either "default" or "7segment"
# TODO: Missing dependency on optional "skin_$(DISPLAYTYPE)_$(BOXTYPE).xml"
skin_display.xml:
	cp $(srcdir)/skin_$(DISPLAYTYPE)_$(BOXTYPE).xml $@ 2>/dev/null || cp $(srcdir)/skin_$(DISPLAYTYPE)_$(TEXTSKIN).xml $@
