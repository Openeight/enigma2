installdir = $(pkglibdir)/python/Plugins/Extensions/ExtrasPanel

SUBDIRS = meta Extra icons locale meta pics

install_PYTHON = *.py

dist_install_DATA = sundtekinstall.sh

if ARM
dist_install_DATA = sundtekinstall.sh
else
dist_install_DATA = sundtekinstall.sh \
	dvbdate
endif

if ARM
install-data-hook:
	@chmod +x $(DESTDIR)$(installdir)/sundtekinstall.sh
else
install-data-hook:
	@chmod +x $(DESTDIR)$(installdir)/sundtekinstall.sh
	@chmod +x $(DESTDIR)$(installdir)/dvbdate
endif
