from Converter import Converter
from Poll import Poll
from enigma import iPlayableService
from Components.Element import cached, ElementError
from time import localtime, strftime, time


class ServicePosition(Poll, Converter, object):
	TYPE_LENGTH = 0
	TYPE_POSITION = 1
	TYPE_REMAINING = 2
	TYPE_GAUGE = 3
	TYPE_SUMMARY = 4
	TYPE_START_END_TIME = 5

	def __init__(self, type):
		Poll.__init__(self)
		Converter.__init__(self, type)

		args = type.split(',')
		type = args.pop(0)

		self.negate = 'Negate' in args
		self.plus = 'Plus' in args
		self.detailed = 'Detailed' in args
		self.showHours = 'ShowHours' in args
		self.showNoSeconds = 'ShowNoSeconds' in args
		self.vfd = '7segment' in args

		if type == "Length":
			self.type = self.TYPE_LENGTH
		elif type == "Position":
			self.type = self.TYPE_POSITION
		elif type == "Remaining":
			self.type = self.TYPE_REMAINING
		elif type == "Gauge":
			self.type = self.TYPE_GAUGE
		elif type == "Summary":
			self.type = self.TYPE_SUMMARY
		elif type == "Startendtime":
			self.type = self.TYPE_START_END_TIME
		else:
			raise ElementError("type must be {Length|Position|Remaining|Gauge|Summary|Startendtime} with optional arguments {Negate|Plus|Detailed|ShowHours|ShowNoSeconds|7segment} for ServicePosition converter")

		if self.detailed:
			self.poll_interval = 100
		elif self.type == self.TYPE_LENGTH or self.type == self.TYPE_START_END_TIME:
			self.poll_interval = 2000
		else:
			self.poll_interval = 500

		self.start_time = self.service = None
		self.poll_enabled = True

	def getSeek(self):
		s = self.source.service
		if self.type == self.TYPE_START_END_TIME and s and (self.service is None or s != self.service):
			self.service = s
			self.start_time = None
		return s and s.seek()

	@cached
	def getPosition(self):
		seek = self.getSeek()
		if seek is None:
			return None
		pos = seek.getPlayPosition()
		if pos[0]:
			return 0
		return pos[1]

	@cached
	def getLength(self):
		seek = self.getSeek()
		if seek is None:
			return None
		length = seek.getLength()
		if length[0]:
			return 0
		return length[1]

	@cached
	def getCutlist(self):
		service = self.source.service
		cue = service and service.cueSheet()
		return cue and cue.getCutList()

	@cached
	def getText(self):
		seek = self.getSeek()
		if seek is None:
			return ""
		else:
			if self.type == self.TYPE_LENGTH:
				l = self.length
			elif self.type == self.TYPE_POSITION:
				l = self.position
			elif self.type == self.TYPE_REMAINING:
				l = self.length - self.position
			elif self.type == self.TYPE_SUMMARY or self.type == self.TYPE_START_END_TIME:
				s = self.position / 90000
				e = (self.length / 90000) - s
				if self.type == self.TYPE_SUMMARY:
					return "%02d:%02d +%2dm" % (s / 60, s % 60, e / 60)
				start_time = strftime("%H:%M", localtime(time() - s))
				end_time = strftime("%H:%M", localtime(time() + e))
				if self.start_time is None:
					self.start_time = start_time
				elif self.start_time != start_time:
					start_time = self.start_time
				return start_time + " - " + end_time

			if l < 0:
				return ""

			if self.negate:
				l = -l

			sign = ""
			if l >= 0:
				if self.plus:
					sign = "+"
			else:
				l = -l
				sign = "-"

			if not self.detailed:
				l /= 90000
				if not self.vfd:
					if self.showHours:
						if self.showNoSeconds:
							return sign + "%d:%02d" % (l / 3600, l % 3600 / 60)
						else:
							return sign + "%d:%02d:%02d" % (l / 3600, l % 3600 / 60, l % 60)
					else:
						if self.showNoSeconds:
							return sign + "%d" % (l / 60)
						else:
							return sign + "%d:%02d" % (l / 60, l % 60)
				else:
					f = l / 60
					if f < 60:
						s = l % 60
					else:
						f /= 60
						s = l % 3600 / 60
					return "%2d:%02d" % (f, s)
			else:
				if self.showHours:
					return sign + "%d:%02d:%02d:%03d" % ((l / 3600 / 90000), (l / 90000) % 3600 / 60, (l / 90000) % 60, (l % 90000) / 90)
				else:
					return sign + "%d:%02d:%03d" % ((l / 60 / 90000), (l / 90000) % 60, (l % 90000) / 90)

	# range/value are for the Progress renderer
	range = 10000

	@cached
	def getValue(self):
		pos = self.position
		len = self.length
		if pos is None or len is None or len <= 0:
			return None
		return pos * 10000 / len

	position = property(getPosition)
	length = property(getLength)
	cutlist = property(getCutlist)
	text = property(getText)
	value = property(getValue)

	def changed(self, what):
		cutlist_refresh = what[0] != self.CHANGED_SPECIFIC or what[1] in (iPlayableService.evCuesheetChanged,)
		time_refresh = what[0] == self.CHANGED_POLL or what[0] == self.CHANGED_SPECIFIC and what[1] in (iPlayableService.evCuesheetChanged,)

		if cutlist_refresh:
			if self.type == self.TYPE_GAUGE:
				self.downstream_elements.cutlist_changed()

		if time_refresh:
			self.downstream_elements.changed(what)
