installdir = $(pkglibdir)/python/Plugins/Extensions/ExtrasPanel

SUBDIRS = meta Extra icons locale meta pics

install_PYTHON = *.py

dist_install_DATA = sundtekinstall.sh ext_lsusb usb.ids

install-data-hook:
	@chmod +x $(DESTDIR)$(installdir)/sundtekinstall.sh

