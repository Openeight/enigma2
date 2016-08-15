installdir = $(pkgdatadir)/display

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
endif
endif

skin_display.xml: $(srcdir)/skin_display_default.xml
	test -f $(srcdir)/skin_display_$(BOXTYPE).xml && cp $(srcdir)/skin_display_$(BOXTYPE).xml skin_display.xml || cp $(srcdir)/skin_display_default.xml skin_display.xml
