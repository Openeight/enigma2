SUBDIRS = countries fonts extensions keymaps skin_default hw_info

dist_pkgdata_DATA = \
	encoding.conf \
	keymap.xml \
	menu.xml \
	prev.png \
	radio.mvi \
	black.mvi \
	rcpositions.xml \
	setup.xml \
	skin_default.xml \
	skin_subtitles.xml \
	skin.xml \
	startwizard.xml \
	freesat.t1 \
	freesat.t2 \
	iso-639-3.pck \
	timezone.xml \
	unicable.xml \
	groupedservices

if HAVE_TEXTLCD
if HAVE_7SEGMENT
SUBDIRS += 7segment
else
dist_pkgdata_DATA += skin_text.xml
endif
else
SUBDIRS += display
endif

iso-639-3.pck: $(srcdir)/iso-639-3.tab
	python $(srcdir)/convert-iso-639-3.py $< $@
