from Components.Converter.Converter import Converter
from Components.Element import cached, ElementError
from enigma import iServiceInformation, eServiceReference
from ServiceReference import ServiceReference


class MovieInfo(Converter):
	MOVIE_SHORT_DESCRIPTION = 0 # meta description when available.. when not .eit short description
	MOVIE_META_DESCRIPTION = 1 # just meta description when available
	MOVIE_REC_SERVICE_NAME = 2 # name of recording service
	MOVIE_REC_FILESIZE = 3 # filesize of recording

	def __init__(self, type):
		if type == "ShortDescription":
			self.type = self.MOVIE_SHORT_DESCRIPTION
		elif type == "MetaDescription":
			self.type = self.MOVIE_META_DESCRIPTION
		elif type == "RecordServiceName":
			self.type = self.MOVIE_REC_SERVICE_NAME
		elif type == "FileSize":
			self.type = self.MOVIE_REC_FILESIZE
		else:
			raise ElementError("'%s' is not <ShortDescription|MetaDescription|RecordServiceName|FileSize> for MovieInfo converter" % type)
		Converter.__init__(self, type)

	@cached
	def getText(self):
		service = self.source.service
		info = self.source.info
		event = self.source.event
		if info and service:
			if self.type == self.MOVIE_SHORT_DESCRIPTION:
				if (service.flags & eServiceReference.flagDirectory) == eServiceReference.flagDirectory:
					# Short description for Directory is the full path
					return service.getPath()
				return (info.getInfoString(service, iServiceInformation.sDescription)
					or (event and event.getShortDescription())
					or service.getPath())
			elif self.type == self.MOVIE_META_DESCRIPTION:
				return ((event and (event.getExtendedDescription() or event.getShortDescription()))
					or info.getInfoString(service, iServiceInformation.sDescription)
					or service.getPath())
			elif self.type == self.MOVIE_REC_SERVICE_NAME:
				rec_ref_str = info.getInfoString(service, iServiceInformation.sServiceref)
				return ServiceReference(rec_ref_str).getServiceName()
			elif self.type == self.MOVIE_REC_FILESIZE:
				if (service.flags & eServiceReference.flagDirectory) == eServiceReference.flagDirectory:
					return _("Directory")
				filesize = info.getInfoObject(service, iServiceInformation.sFileSize)
				if filesize is not None:
					if filesize >= 104857600000: #100000*1024*1024
						return _("%.0f GB") % (filesize / 1073741824.0)
					elif filesize >= 1073741824: #1024*1024*1024
						return _("%.2f GB") % (filesize / 1073741824.0)
					elif filesize >= 1048576:
						return _("%.0f MB") % (filesize / 1048576.0)
					elif filesize >= 1024:
						return _("%.0f kB") % (filesize / 1024.0)
					return _("%d B") % filesize
		return ""

	text = property(getText)
