SUBDIRS = LCDAnalogClock_1_Standby LCDAnalogClock_2_Standby LCDWeather_Standby

installdir = $(pkgdatadir)/display

if HAVE_COLORLCD
dist_install_DATA = skin_display96.xml
else
dist_install_DATA = skin_display.xml
endif

skin_display.xml: $(srcdir)/skin_display_default.xml
	test -f $(srcdir)/skin_display_$(BOXTYPE).xml && cp $(srcdir)/skin_display_$(BOXTYPE).xml skin_display.xml || cp $(srcdir)/skin_display_default.xml skin_display.xml
