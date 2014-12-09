#Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/OpenXtaReader/Xtrend.py
from Components.ActionMap import ActionMap, NumberActionMap
from Components.config import config
from Components.Input import Input
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmap, MultiContentEntryPixmapAlphaTest, MultiContentEntryPixmapAlphaBlend
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from enigma import eConsoleAppContainer, eListboxPythonMultiContent, eListbox, ePicLoad, eTimer, getDesktop, gFont, loadPic, loadPNG, RT_HALIGN_LEFT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eEnv
from Plugins.Plugin import PluginDescriptor
from re import findall, match, search, split, sub
from Screens.Console import Console
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.VirtualKeyBoard import VirtualKeyBoard
from string import find, atoi, strip
from Tools.Directories import fileExists
from twisted.web import client, error
from twisted.web.client import getPage, downloadPage
import os, re, sys, time, urllib
from os import system

def transHTML(text):
	text = text.replace('&nbsp;', ' ').replace('&#33;', '!').replace('&#034;', '"').replace('&#039;', "'").replace('&szlig;', 'ss').replace('&quot;', '"').replace('&ndash;', '-').replace('&Oslash;', '').replace('&bdquo;', '"').replace('&ldquo;', '"').replace('&#8211;', '-').replace('&laquo;', '\xc2\xab').replace('&raquo;', '\xc2\xbb').replace('&rdquo;', '"').replace('&rsquo;', "'").replace('&sup2;', '\xc2\xb2').replace('&bull;', '\xe2\x80\xa2').replace('&euro;', '\xe2\x82\xac').replace('&reg;', '\xc2\xae')
	text = text.replace('&copy;.*', ' ').replace('&amp;', '&').replace('&uuml;', '\xc3\xbc').replace('&auml;', '\xc3\xa4').replace('&ouml;', '\xc3\xb6').replace('&hellip;', '...').replace('&deg;', '\xc2\xb0').replace('&acute;', "'").replace('&aacute;', '\xc3\xa1').replace('&eacute;', '\xc3\xa9').replace('&iacute;', '\xc3\xad').replace('&oacute;', '\xc3\xb3').replace('&egrave;', '\xc3\xa8').replace('&agrave;', '\xc3\xa0').replace('&lt;', '\xc2\xab').replace('&gt;', '\xc2\xbb').replace('&iquest;', '\xc2\xbf')
	text = text.replace('&Uuml;', '\xc3\x9c').replace('&Auml;', '\xc3\x84').replace('&Ouml;', '\xc3\x96').replace('&#34;', '"').replace('&#38;', 'und').replace('&#39;', "'").replace('&#196;', 'Ae').replace('&#214;', 'Oe').replace('&#220;', 'Ue').replace('&#223;', 'ss').replace('&#228;', '\xc3\xa4').replace('&#246;', '\xc3\xb6').replace('&#252;', '\xc3\xbc').replace('&copy;', '\xc2\xa9').replace('&#8364;', '\xe2\x82\xac')
	text = text.replace('&#60;','<').replace('&#62;','>')
	return text

def convertDate(date):
	if date[0:5] == 'Today':
		return 'Today'
	elif date[0:9] == 'Yesterday':
		return 'Yesterday'
	dd = date[0:2]
	mm = date[3:6]
	if mm == 'Jan':
		mm = '01'
	elif mm == 'Feb':
		mm = '02'
	elif mm == 'Mar':
		mm = '03'
	elif mm == 'Apr':
		mm = '04'
	elif mm == 'May':
		mm = '05'
	elif mm == 'Jun':
		mm = '06'
	elif mm == 'Jul':
		mm = '07'
	elif mm == 'Aug':
		mm = '08'
	elif mm == 'Sep':
		mm = '09'
	elif mm == 'Oct':
		mm = '10'
	elif mm == 'Nov':
		mm = '11'
	elif mm == 'Dec':
		mm = '12'
	yy = date[9:11]
	return dd + '-' + mm + '-' + yy

class OpenXtaThread(Screen):
	skin = '\n\t\t\t<screen position="center,center" size="620,510" backgroundColor="#161616" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/Xtrend.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,102" size="600,400" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="textpage" position="10,107" size="600,400" backgroundColor="#161616" foregroundColor="#FFFFFF" font="Regular;20" halign="left" zPosition="1" />\n\t\t\t</screen>'
	skinwhite = '\n\t\t\t<screen position="center,center" size="620,510" backgroundColor="#FFFFFF" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/Xtrend_white.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,102" size="600,400" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="textpage" position="10,107" size="600,400" backgroundColor="#FFFFFF" foregroundColor="#000000" font="Regular;20" halign="left" zPosition="1" />\n\t\t\t</screen>'
	skinHD = '\n\t\t\t<screen position="center,60" size="820,637" backgroundColor="#161616" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/XtrendHD.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,127" size="800,500" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="textpage" position="10,127" size="800,500" backgroundColor="#161616" foregroundColor="#FFFFFF" font="Regular;22" halign="left" zPosition="1" />\n\t\t\t</screen>'
	skinHDwhite = '\n\t\t\t<screen position="center,60" size="820,637" backgroundColor="#FFFFFF" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/XtrendHD_white.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,127" size="800,500" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="textpage" position="10,127" size="800,500" backgroundColor="#FFFFFF" foregroundColor="#000000" font="Regular;22" halign="left" zPosition="1" />\n\t\t\t</screen>'

	def __init__(self, session, link, fav, portal):
		self.colorfile = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/db/color')
		if fileExists(self.colorfile):
			f = open(self.colorfile, 'r')
			if 'white' in f:
				self.white = True
			else:
				self.white = False
			f.close()
		else:
			self.white = False
		deskWidth = getDesktop(0).size().width()
		if deskWidth == 1280 and self.white == False:
			self.skin = OpenXtaThread.skinHD
			self.xd = False
		elif deskWidth == 1280 and self.white == True:
			self.skin = OpenXtaThread.skinHDwhite
			self.xd = False
		elif deskWidth <= 1025 and self.white == False:
			self.skin = OpenXtaThread.skin
			self.xd = True
		elif deskWidth <= 1025 and self.white == True:
			self.skin = OpenXtaThread.skinwhite
			self.xd = True
		Screen.__init__(self, session)
		self.hideflag = True
		self.closed = False
		self.lastpage = True
		self.ready = False
		self.level = False
		self.fav = fav
		self.portal = portal
		self.count = 1
		self.maxcount = 1
		self.postcount = 1
		self.maxpostcount = 1
		self.threadtitle = ''
		self.link = link
		self.postlink = ''
		self.linkback = ''
		self.titellist = []
		self.threadlink = []
		self.threadentries = []
		self['menu'] = ItemList([])
		self['menu'].hide()
		self['textpage'] = ScrollLabel('')
		self['textpage'].hide()
		self.current = 'menu'
		self['NumberActions'] = NumberActionMap(['NumberActions',
		 'OkCancelActions',
		 'DirectionActions',
		 'ColorActions',
		 'ChannelSelectBaseActions',
		 'MovieSelectionActions',
		 'HelpActions'], {'ok': self.ok,
		 'cancel': self.exit,
		 'down': self.down,
		 'up': self.up,
		 'right': self.rightDown,
		 'left': self.leftUp,
		 'nextBouquet': self.nextPage,
		 'prevBouquet': self.prevPage,
		 '0': self.gotoPage,
		 '1': self.gotoPage,
		 '2': self.gotoPage,
		 '3': self.gotoPage,
		 '4': self.gotoPage,
		 '5': self.gotoPage,
		 '6': self.gotoPage,
		 '7': self.gotoPage,
		 '8': self.gotoPage,
		 '9': self.gotoPage,
		 'yellow': self.infoScreen,
		 'red': self.red,
		 'green': self.infoScreen,
		 'blue': self.hideScreen,
		 'showEventInfo': self.showHelp,
		 'contextMenu': self.showHelp,
		 'displayHelp': self.infoScreen}, -1)
		self.makeThreadTimer = eTimer()
		if fav == False:
			self.makeThreadTimer.callback.append(self.download(self.link, self.makeThreadView))
		else:
			self.current = 'postview'
			self.postlink = link
			self.makeThreadTimer.callback.append(self.download(self.postlink, self.makeLastPage))
		self.makeThreadTimer.start(500, True)

	def makeThreadView(self, output):
		if self.portal == False:
			startpos = find(output, '<!-- __-SUBFORUMS-__ -->')
			endpos = find(output, '<div id=\'forum_footer\'')
			bereich = output[startpos:endpos]
			bereich = sub('<td class=\'col_f_content \'>\s*?<span class=\'ipsBadge ipsBadge_green\'>Pinned</span>', '<logo>thread_sticky-30</logo>', bereich)
			bereich = sub('<td class=\'col_c_icon\'>', '<logo>thread_old-30</logo>', bereich)
			bereich = sub('<td class=\'col_f_content \'>\s*?<h4>', '<logo>thread_old-30</logo>', bereich)

			bereich = sub('<td class=\'col_c_forum\'>\s*?<h4>\s*?<a href="(.*?)" title=\'(.*?)\'', '<link>\g<1></link><titel>\g<2></titel>', bereich)
			bereich = sub('<span itemprop="name">(.*?)</span>', '<titel>\g<1></titel>', bereich)

			bereich = sub('<meta itemprop="interactionCount" content="UserComments:', '<stats>Replies: ', bereich)
			bereich = sub('"/>\s*?</li>\s*?<li class=\'views desc\'>',', Views: ', bereich)
			bereich = sub(' Views</li>', '</stats>', bereich)
			bereich = sub('<li><strong>(.*?)</strong> topics</li>\s*?<li>', '<stats>Threads: \g<1>', bereich)
			bereich = sub('<strong>(.*?)</strong> replies</li>', ' Posts: \g<1></stats>', bereich)

			bereich = sub('<ul class=\'last_post ipsType_small\'>\s*?<li>\s*?([a-zA-Z0-9_ ]*?)\s*?</li>', '<user>\g<1></user>', bereich)
			bereich = sub('<li>By \n\t(.*?)\s*?</li>', '<user>\g<1></user>', bereich)

			bereich = sub('<a itemprop="url" id=".*?" href="(.*?)"', '<link>\g<1></link>', bereich)

			bereich = transHTML(bereich)
			if search('<a href=\'\#\'>Page 1 of [0-9]+ <!--<img', output) is not None:
				page = search('Page 1 of ([0-9]+) <!--<img', output)
				self.maxcount = int(page.group(1))
			title = search('<title>(.*?)</title>', output)
			title = title.group(1)
			title = transHTML(title)
			title = title + ' | Seite ' + str(self.count) + ' von ' + str(self.maxcount)
			self.threadtitle = title
			self.setTitle(title)
		else:
			startpos = find(output, '<!-- ::: CONTENT ::: -->')
			endpos = find(output, '</table>')
			bereich = output[startpos:endpos]
			bereich = transHTML(bereich)

			bereich = sub('<td class=\'col_f_icon short altrow\'>', '<logo>thread_old-30</logo>', bereich)

			bereich = sub('<h4><a href=\'(.*?)\' title=\'View result\'>(.*?)</a></h4>', '<link>\g<1></link><titel>\g<2></titel>', bereich)

			bereich = sub('<td class=\'col_f_views\'>\s*?<ul>\s*?<li>(.*?) repl.*?</li>\s*?<li class=\'views desc\'>(.*?) views</li>\s*?</ul>\s*?</td>', '<stats>Replies: \g<1>, Views: \g<2></stats>', bereich)

			bereich = sub('<ul class=\'last_post ipsType_small\'>\s*?<li>\s*?([a-zA-Z0-9_ ]*?)\s*?</li>', '<user>\g<1></user>', bereich)
			self.setTitle(_("Latest Posts"))
		logo = re.findall('<logo>(.*?)</logo>', bereich)
		titel = re.findall('<titel>(.*?)</titel>', bereich)
		stats = re.findall('<stats>(.*?)</stats>', bereich)
		date = re.findall('\?view=getlastpost\' title=\'(?:Go to|View) last post.*?\'>\s*?([a-zA-Z0-9,:_ ]*?)\s*?</a>', bereich)
		user = re.findall('<user>(.*?)</user>', bereich)
		link = re.findall('<link>(.*?)</link>', bereich)
		idx = 0
		for x in titel:
			idx += 1

		for i in range(idx):
			try:
				x = ''
				res = [x]
				if self.xd == True:
					if self.white == True:
						line = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/line_gray.png')
						if fileExists(line):
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(600, 1), png=loadPNG(line)))
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(600, 1), png=loadPNG(line)))
						res.append(MultiContentEntryText(pos=(0, 1), size=(45, 48), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=0, flags=RT_HALIGN_LEFT, text=''))
						res.append(MultiContentEntryText(pos=(45, 1), size=(555, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=titel[i]))
						res.append(MultiContentEntryText(pos=(45, 25), size=(340, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=stats[i]))
						res.append(MultiContentEntryText(pos=(385, 25), size=(105, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=convertDate(date[i])))
						res.append(MultiContentEntryText(pos=(490, 25), size=(110, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=user[i]))
						if convertDate(date[i]) == 'Today':
							png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/thread_new-30.png')
							if fileExists(png):
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
						else:
							png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/%s.png') % logo[i]
							if fileExists(png):
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
					else:
						line = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/line_white.png')
						if fileExists(line):
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(600, 1), png=loadPNG(line)))
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(600, 1), png=loadPNG(line)))
						res.append(MultiContentEntryText(pos=(45, 1), size=(555, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=titel[i]))
						res.append(MultiContentEntryText(pos=(45, 25), size=(340, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=stats[i]))
						res.append(MultiContentEntryText(pos=(385, 25), size=(105, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=convertDate(date[i])))
						res.append(MultiContentEntryText(pos=(490, 25), size=(110, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=user[i]))
						if convertDate(date[i]) == 'Today':
							png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/thread_new-30.png')
							if fileExists(png):
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
						else:
							png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/%s.png') % logo[i]
							if fileExists(png):
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
				elif self.white == True:
					line = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/line_gray.png')
					if fileExists(line):
						res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(800, 1), png=loadPNG(line)))
						res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(800, 1), png=loadPNG(line)))
					res.append(MultiContentEntryText(pos=(0, 1), size=(45, 48), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=0, flags=RT_HALIGN_LEFT, text=''))
					res.append(MultiContentEntryText(pos=(45, 1), size=(755, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=titel[i]))
					res.append(MultiContentEntryText(pos=(45, 25), size=(485, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=stats[i]))
					res.append(MultiContentEntryText(pos=(530, 25), size=(120, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=convertDate(date[i])))
					res.append(MultiContentEntryText(pos=(650, 25), size=(150, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=user[i]))
					if convertDate(date[i]) == 'Today':
						png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/thread_new-30.png')
						if fileExists(png):
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
					else:
						png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/%s.png') % logo[i]
						if fileExists(png):
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
				else:
					line = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/line_white.png')
					if fileExists(line):
						res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(800, 1), png=loadPNG(line)))
						res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(800, 1), png=loadPNG(line)))
					res.append(MultiContentEntryText(pos=(45, 1), size=(755, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=titel[i]))
					res.append(MultiContentEntryText(pos=(45, 25), size=(485, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=stats[i]))
					res.append(MultiContentEntryText(pos=(530, 25), size=(120, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=convertDate(date[i])))
					res.append(MultiContentEntryText(pos=(650, 25), size=(150, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=user[i]))
					if convertDate(date[i]) == 'Today':
						png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/thread_new-30.png')
						if fileExists(png):
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
					else:
						png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/%s.png') % logo[i]
						if fileExists(png):
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
				self.titellist.append(titel[i])
				self.threadlink.append(link[i])
				self.threadentries.append(res)
			except IndexError:
				pass

		self['menu'].l.setList(self.threadentries)
		self['menu'].l.setItemHeight(50)
		self['menu'].moveToIndex(0)
		self['menu'].show()
		self.ready = True

	def makePostviewPage(self, output):
		self['menu'].hide()
		startpos = find(output, '<!-- ::: CONTENT ::: -->')
		endpos = find(output, '<!-- Close topic -->')
		bereich = output[startpos:endpos]
		bereich = transHTML(bereich)
		title = search('<title>(.*?)</title>', output)
		title = title.group(1)
		title = transHTML(title)
		if self.xd == True:
			title = title[0:40] + '... | Seite ' + str(self.postcount) + ' von ' + str(self.maxpostcount)
		else:
			title = title[0:45] + '... | Seite ' + str(self.postcount) + ' von ' + str(self.maxpostcount)
		self.setTitle(title)
		bereich = sub('<br />', '</p><p>', bereich)
		bereich = sub('<a href="http://www.xtrend-alliance.com/index.php\?app=core&module=attach&section=attach&attach_id=.*?" title="Download attachment"><strong>(.*?)</strong></a>', '<p>Attachment: \g<1></p>', bereich)
		bereich = sub('<img src=\'http://www.xtrend-alliance.com/public/style_emoticons/default/.*?\' class=\'bbc_emoticon\' alt=\'(.*?)\' /x>', '<p>Smilie: \g<1>', bereich)
		bereich = sub('<script type=\'text/javascript\'>\s*?.*?\s*?</script>', '', bereich)
		bereich = sub('<p class=\'posted_info desc lighter ipsType_small\'>', '<p>', bereich) # posted date
		bereich = sub('<span class=\'hide\' itemprop="name">(.*?)</span>\s*?<ul class=\'basic_info\'>\s*?<p class=\'desc member_title\'>(.*?)</p>', '<p>\g<1>, \g<2></p>', bereich) # user name, status
		bereich = sub('<blockquote  class="ipsBlockquote" data-author=".*?" data-cid=".*?" data-time=".*?">([\s\S]*?)</blockquote>', '<p>Quote: \g<1> :Quote end</p>', bereich) # quote 1
		bereich = sub('(<p>Quote: )[[\s\S]*?<p>([\s\S]*?)</p>[\s\S]*?]*( :Quote end</p>)', '\g<1>\g<2>\g<3>', bereich) # quote 2
		bereich = sub('<li id="like_post_.*?" class=\'ipsLikeBar_info\' >\s*?.*?\s*?</li>', '', bereich) # del likes
		bereich = sub('<span>Please log in to reply</span>', '', bereich) # del "Please log in to reply"
		bereich = sub('<span class=\'ipsType_small\'>\s*?.*?to this topic.*?\s*?</span>', '', bereich) # del # replies
		bereich = sub('<div class=\"signature\".*?\s*?.*?\s*?</div>', '', bereich) # del signature
		bereich = sub('<div class=\'pagination clearfix left \'>[\s\S]*?</div>', '', bereich) # del page quick links 1, 2, 3....
		bereich = sub('<span>(.*?)</span>', '\g<1>', bereich)
		if self.xd == True:
			bereich = sub('<ul id=\'postControlsNormal_[0-9]*\' class=\'post_controls clear clearfix\' >', '<p>\n==============================================</p>', bereich)
		else:
			bereich = sub('<ul id=\'postControlsNormal_[0-9]*\' class=\'post_controls clear clearfix\' >', '<p>\n===========================================================</p>', bereich)
		text = ''
		a = findall('<p>(.*?)</p>', bereich, re.S)
		for x in a:
			if x != '':
				text = text + x + '\n'

		text = sub('<[^>]*>', ' ', text)
		text = sub('</p<<p<', '\n\n', text)
		text = sub('\n\\s+\n*', '\n\n', text)
		self['textpage'].setText(text)
		self['textpage'].show()
		if self.lastpage == True:
			self['textpage'].lastPage()
			self['textpage'].pageUp()

	def ok(self):
		if self.current == 'menu':
			try:
				c = self['menu'].getSelectedIndex()
				self.postlink = self.threadlink[c]
				if search('index.php/forum', self.postlink) is not None:
					self.level = True
					self.titellist = []
					self.threadlink = []
					self.threadentries = []
					self.linkback = self.link
					self.link = self.postlink
					self.download(self.link, self.makeThreadView)
				else:
					self.current = 'postview'
					self.lastpage = True
					self.download(self.postlink, self.makeLastPage)
			except IndexError:
				pass

	def red(self):
		if self.ready == True:
			try:
				c = self['menu'].getSelectedIndex()
				name = self.titellist[c]
				self.session.openWithCallback(self.red_return, MessageBox, _("\nPost '%s' zu den Favoriten hinzuf\xc3\xbcgen?") % name, MessageBox.TYPE_YESNO)
			except IndexError:
				pass

	def red_return(self, answer):
		if answer is True:
			c = self['menu'].getSelectedIndex()
			favoriten = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/db/favoriten')
			if fileExists(favoriten):
				f = open(favoriten, 'a')
				data = self.titellist[c] + ':::' + self.threadlink[c]
				f.write(data)
				f.write(os.linesep)
				f.close()
			self.session.open(OpenXtaFav)

	def makeLastPage(self, output):
		if search('<a href=\'\#\'>Page 1 of [0-9]+ <!--<img', output) is not None:
			page = re.findall('Page 1 of ([0-9]+) <!--<img', output)
			try:
				self.postcount = int(page[0])
				self.maxpostcount = int(page[0])
				link = self.postlink + '/page-' + page[0]
				self.download(link, self.makePostviewPage)
			except IndexError:
				self.download(self.postlink, self.makePostviewPage)

		else:
			self.postcount = 1
			self.maxpostcount = 1
			self.download(self.postlink, self.makePostviewPage)

	def nextPage(self):
		if self.current == 'menu':
			self.count += 1
			if self.count >= self.maxcount:
				self.count = self.maxcount
			link = self.link + '/page-' + str(self.count)
			self.titellist = []
			self.threadlink = []
			self.threadentries = []
			self['menu'].hide()
			self.makeThreadTimer.callback.append(self.download(link, self.makeThreadView))
		else:
			self.lastpage = False
			self.postcount += 1
			if self.postcount >= self.maxpostcount:
				self.postcount = self.maxpostcount
			link = self.postlink + '/page-' + str(self.postcount)
			self.download(link, self.makePostviewPage)

	def prevPage(self):
		if self.current == 'menu':
			self.count -= 1
			if self.count == 0:
				self.count = 1
			link = self.link + '/page-' + str(self.count)
			self.titellist = []
			self.threadlink = []
			self.threadentries = []
			self['menu'].hide()
			self.makeThreadTimer.callback.append(self.download(link, self.makeThreadView))
		else:
			self.lastpage = True
			self.postcount -= 1
			if self.postcount == 0:
				self.postcount = 1
			link = self.postlink + '/page-' + str(self.postcount)
			self.download(link, self.makePostviewPage)

	def gotoPage(self, number):
		self.session.openWithCallback(self.numberEntered, getNumber, number)

	def numberEntered(self, number):
		if self.current == 'menu':
			if number is None or number == 0:
				pass
			else:
				if int(number) > self.maxcount:
					number = self.maxcount
					if number > 1:
						self.session.open(MessageBox, '\nNur %s Seiten verf\xc3\xbcgbar. Gehe zu Seite %s.' % (number, number), MessageBox.TYPE_INFO, timeout=3)
					else:
						self.session.open(MessageBox, '\nNur %s Seite verf\xc3\xbcgbar. Gehe zu Seite %s.' % (number, number), MessageBox.TYPE_INFO, timeout=3)
				self.count = int(number)
				link = self.link + '/page-' + str(self.count)
				self.titellist = []
				self.threadlink = []
				self.threadentries = []
				self['menu'].hide()
				self.makeThreadTimer.callback.append(self.download(link, self.makeThreadView))
		elif number is None or number == 0:
			pass
		else:
			self.lastpage = False
			if int(number) > self.maxpostcount:
				number = self.maxpostcount
				if number > 1:
					self.session.open(MessageBox, '\nNur %s Seiten verf\xc3\xbcgbar. Gehe zu Seite %s.' % (number, number), MessageBox.TYPE_INFO, timeout=5)
				else:
					self.session.open(MessageBox, '\nNur %s Seite verf\xc3\xbcgbar. Gehe zu Seite %s.' % (number, number), MessageBox.TYPE_INFO, timeout=5)
			self.postcount = int(number)
			link = self.postlink + '/page-' + str(self.postcount)
			self.download(link, self.makePostviewPage)

	def showHelp(self):
		self.session.open(MessageBox, '\n%s' % '0 - 999 = Seite\nBouquet = +- Seite\nRot = Zu Favoriten hinzuf\xc3\xbcgen\nHelp = Update Check', MessageBox.TYPE_INFO)

	def selectMenu(self):
		self['menu'].selectionEnabled(1)

	def down(self):
		if self.current == 'menu':
			self['menu'].down()
		else:
			self['textpage'].pageDown()

	def up(self):
		if self.current == 'menu':
			self['menu'].up()
		else:
			self['textpage'].pageUp()

	def rightDown(self):
		if self.current == 'menu':
			self['menu'].pageDown()
		else:
			self['textpage'].pageDown()

	def leftUp(self):
		if self.current == 'menu':
			self['menu'].pageUp()
		else:
			self['textpage'].pageUp()

	def download(self, link, name):
		getPage(link).addCallback(name).addErrback(self.downloadError)

	def downloadError(self, output):
		pass

	def infoScreen(self):
		self.session.open(infoOpenXta)

	def hideScreen(self):
		if self.hideflag == True:
			self.hideflag = False
			count = 40
			while count > 0:
				count -= 1
				f = open('/proc/stb/video/alpha', 'w')
				f.write('%i' % (config.av.osd_alpha.value * count / 40))
				f.close()

		else:
			self.hideflag = True
			count = 0
			while count < 40:
				count += 1
				f = open('/proc/stb/video/alpha', 'w')
				f.write('%i' % (config.av.osd_alpha.value * count / 40))
				f.close()

	def exit(self):
		if self.hideflag == False:
			f = open('/proc/stb/video/alpha', 'w')
			f.write('%i' % config.av.osd_alpha.value)
			f.close()
		if self.fav == True:
			self.close()
		elif self.current == 'postview':
			self['textpage'].hide()
			self['menu'].show()
			self.current = 'menu'
			self.setTitle(self.threadtitle)
			self.lastpage = True
		elif self.level == True:
			self.link = self.linkback
			self.level = False
			self.titellist = []
			self.threadlink = []
			self.threadentries = []
			self.download(self.link, self.makeThreadView)
		else:
			self.close()


class getNumber(Screen):
	skin = '\n\t\t\t<screen position="center,center" size="185,55" backgroundColor="background" flags="wfNoBorder" title=" ">\n\t\t\t\t<widget name="number" position="0,0" size="185,55" font="Regular;30" halign="center" valign="center" transparent="1" zPosition="1"/>\n\t\t\t</screen>'

	def __init__(self, session, number):
		Screen.__init__(self, session)
		self.field = str(number)
		self['number'] = Label(self.field)
		self['actions'] = NumberActionMap(['SetupActions'], {'cancel': self.quit,
		 'ok': self.keyOK,
		 '1': self.keyNumber,
		 '2': self.keyNumber,
		 '3': self.keyNumber,
		 '4': self.keyNumber,
		 '5': self.keyNumber,
		 '6': self.keyNumber,
		 '7': self.keyNumber,
		 '8': self.keyNumber,
		 '9': self.keyNumber,
		 '0': self.keyNumber})
		self.Timer = eTimer()
		self.Timer.callback.append(self.keyOK)
		self.Timer.start(2000, True)

	def keyNumber(self, number):
		self.Timer.start(2000, True)
		self.field = self.field + str(number)
		self['number'].setText(self.field)
		if len(self.field) >= 4:
			self.keyOK()

	def keyOK(self):
		self.Timer.stop()
		self.close(int(self['number'].getText()))

	def quit(self):
		self.Timer.stop()
		self.close(0)


class OpenXtaFav(Screen):
	skin = '\n\t\t\t<screen position="center,center" size="620,510" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/Xtrend.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="label" position="258,100" size="250,20" font="Regular;16" foregroundColor="#FFFFFF" backgroundColor="#000000" halign="left" transparent="1" zPosition="2" />\n\t\t\t\t<ePixmap position="234,100" size="18,48" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/buttons/red.png') + '" alphatest="blend" zPosition="2" />\n\t\t\t\t<widget name="favmenu" position="10,130" size="600,375" scrollbarMode="showOnDemand" zPosition="1" />\n\t\t\t</screen>'
	skinwhite = '\n\t\t\t<screen position="center,center" size="620,510" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/Xtrend_white.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="label" position="258,100" size="250,20" font="Regular;16" foregroundColor="#FFFFFF" backgroundColor="#000000" halign="left" transparent="1" zPosition="2" />\n\t\t\t\t<ePixmap position="234,100" size="18,48" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/buttons/red.png') + '" alphatest="blend" zPosition="2" />\n\t\t\t\t<widget name="favmenu" position="10,130" size="600,375" scrollbarMode="showOnDemand" zPosition="1" />\n\t\t\t</screen>'
	skinHD = '\n\t\t\t<screen position="center,60" size="820,637" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/XtrendHD.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="label" position="343,127" size="250,22" font="Regular;18" foregroundColor="#FFFFFF" backgroundColor="#000000" halign="left" transparent="1" zPosition="2" />\n\t\t\t\t<ePixmap position="319,127" size="18,65" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/buttons/red.png') + '" alphatest="blend" zPosition="2" />\n\t\t\t\t<widget name="favmenu" position="10,157" size="800,475" scrollbarMode="showOnDemand" zPosition="1" />\n\t\t\t</screen>'
	skinHDwhite = '\n\t\t\t<screen position="center,60" size="820,637" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/XtrendHD_white.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="label" position="343,127" size="250,22" font="Regular;18" foregroundColor="#FFFFFF" backgroundColor="#000000" halign="left" transparent="1" zPosition="2" />\n\t\t\t\t<ePixmap position="319,127" size="18,65" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/buttons/red.png') + '" alphatest="blend" zPosition="2" />\n\t\t\t\t<widget name="favmenu" position="10,157" size="800,475" scrollbarMode="showOnDemand" zPosition="1" />\n\t\t\t</screen>'

	def __init__(self, session):
		self.colorfile = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/db/color')
		if fileExists(self.colorfile):
			f = open(self.colorfile, 'r')
			if 'white' in f:
				self.white = True
			else:
				self.white = False
			f.close()
		else:
			self.white = False
		deskWidth = getDesktop(0).size().width()
		if deskWidth == 1280 and self.white == False:
			self.skin = OpenXtaFav.skinHD
			self.xd = False
		elif deskWidth == 1280 and self.white == True:
			self.skin = OpenXtaFav.skinHDwhite
			self.xd = False
		elif deskWidth <= 1025 and self.white == False:
			self.skin = OpenXtaFav.skin
			self.xd = True
		elif deskWidth <= 1025 and self.white == True:
			self.skin = OpenXtaFav.skinwhite
			self.xd = True
		self.session = session
		Screen.__init__(self, session)
		self.favlist = []
		self.favlink = []
		self.hideflag = True
		self.count = 0
		self['favmenu'] = MenuList([])
		self['label'] = Label('= Entferne Favorit')
		self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions'], {'ok': self.ok,
		 'cancel': self.exit,
		 'down': self.down,
		 'up': self.up,
		 'red': self.red,
		 'yellow': self.infoScreen,
		 'green': self.infoScreen,
		 'blue': self.hideScreen}, -1)
		self.makeFav()

	def makeFav(self):
		self.setTitle('OpenXTA:::Favoriten')
		self.favoriten = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/db/favoriten')
		if fileExists(self.favoriten):
			f = open(self.favoriten, 'r')
			for line in f:
				if ':::' in line:
					self.count += 1
					favline = line.split(':::')
					id = self.count
					titel = str(favline[0])
					link = favline[1].replace('\n', '')
					self.favlist.append(titel)
					self.favlink.append(link)

			f.close()
			self['favmenu'].l.setList(self.favlist)

	def ok(self):
		try:
			c = self.getIndex(self['favmenu'])
			link = self.favlink[c]
			if search('index.php/forum', link) is None:
				self.session.openWithCallback(self.exit, OpenXtaThread, link, True, False)
			else:
				self.session.openWithCallback(self.exit, OpenXtaThread, link, False, False)
		except IndexError:
			pass

	def red(self):
		if len(self.favlist) > 0:
			try:
				c = self.getIndex(self['favmenu'])
				name = self.favlist[c]
			except IndexError:
				name = ''

			self.session.openWithCallback(self.red_return, MessageBox, _("\nPost '%s' aus den Favoriten entfernen?") % name, MessageBox.TYPE_YESNO)

	def red_return(self, answer):
		if answer is True:
			c = self.getIndex(self['favmenu'])
			try:
				link = self.favlink[c]
			except IndexError:
				link = 'NONE'

			data = ''
			f = open(self.favoriten, 'r')
			for line in f:
				if link not in line and line != '\n':
					data = data + line

			f.close()
			fnew = open(self.favoriten + '.new', 'w')
			fnew.write(data)
			fnew.close()
			os.rename(self.favoriten + '.new', self.favoriten)
			self.favlist = []
			self.favlink = []
			self.makeFav()

	def getIndex(self, list):
		return list.getSelectedIndex()

	def down(self):
		self['favmenu'].down()

	def up(self):
		self['favmenu'].up()

	def infoScreen(self):
		self.session.open(infoOpenXta)

	def hideScreen(self):
		if self.hideflag == True:
			self.hideflag = False
			count = 40
			while count > 0:
				count -= 1
				f = open('/proc/stb/video/alpha', 'w')
				f.write('%i' % (config.av.osd_alpha.value * count / 40))
				f.close()

		else:
			self.hideflag = True
			count = 0
			while count < 40:
				count += 1
				f = open('/proc/stb/video/alpha', 'w')
				f.write('%i' % (config.av.osd_alpha.value * count / 40))
				f.close()

	def exit(self):
		if self.hideflag == False:
			f = open('/proc/stb/video/alpha', 'w')
			f.write('%i' % config.av.osd_alpha.value)
			f.close()
		self.close()


class infoOpenXta(Screen):
	skin = '\n\t\t\t\t<screen position="center,center" size="425,425" title="OpenXTA Forum Reader 0.3" >\n\t\t\t\t\t<ePixmap position="0,0" size="425,425" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/info.png') + '" zPosition="1"/>\n\t\t\t\t\t<widget name="label" position="0,62" size="425,350" font="Regular;18" foregroundColor="#E5382F" backgroundColor="#161616" halign="center" valign="center" transparent="1" zPosition="2" />\n\t\t\t\t</screen>'
	skinwhite = '\n\t\t\t\t<screen position="center,center" size="425,425" title="OpenXTA Forum Reader 0.3" >\n\t\t\t\t\t<ePixmap position="0,0" size="425,425" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/info_white.png') + '" zPosition="1"/>\n\t\t\t\t\t<widget name="label" position="0,62" size="425,350" font="Regular;18" foregroundColor="#D42828" backgroundColor="#FFFFFF" halign="center" valign="center" transparent="1" zPosition="2" />\n\t\t\t\t</screen>'

	def __init__(self, session):
		self.colorfile = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/db/color')
		if fileExists(self.colorfile):
			f = open(self.colorfile, 'r')
			if 'white' in f:
				self.white = True
			else:
				self.white = False
			f.close()
		else:
			self.white = False
		if self.white == False:
			self.skin = infoOpenXta.skin
		else:
			self.skin = infoOpenXta.skinwhite
		Screen.__init__(self, session)
		self['label'] = Label('Angepassung f\xc3\xbcrs OpenXTA\nmade by Betacentauri\nwww.kashmir-plugins.de\nGef\xc3\xa4llt Ihnen das Plugin?\nM\xc3\xb6chten Sie etwas spenden?\nGehen Sie dazu bitte wie folgt vor:\n\n\n\n1. Melden Sie sich bei PayPal an\n2. Klicken Sie auf: Geld senden\n3. Adresse: paypal@kashmir-plugins.de\n4. Betrag: 5 Euro\n5. Weiter\n6. Geld senden\nDanke!')
		self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.close,
		 'cancel': self.close}, -1)


class ItemList(MenuList):

	def __init__(self, items, enableWrapAround = True):
		MenuList.__init__(self, items, enableWrapAround, eListboxPythonMultiContent)
		self.l.setFont(-1, gFont('Regular', 22))
		self.l.setFont(0, gFont('Regular', 20))
		self.l.setFont(1, gFont('Regular', 18))
		self.l.setFont(2, gFont('Regular', 16))


class OpenXtaMain(Screen):
	skin = '\n\t\t\t<screen position="center,center" size="620,510" backgroundColor="#161616" title="OpenXTA Forum">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/Xtrend.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,102" size="600,400" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="user" position="10,107" size="600,400" backgroundColor="#161616" foregroundColor="#FFFFFF" font="Regular;20" halign="left" zPosition="1" />\n\t\t\t</screen>'
	skinwhite = '\n\t\t\t<screen position="center,center" size="620,510" backgroundColor="#FFFFFF" title="OpenXTA Forum">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/Xtrend_white.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,102" size="600,400" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="user" position="10,107" size="600,400" backgroundColor="#FFFFFF" foregroundColor="#000000" font="Regular;20" halign="left" zPosition="1" />\n\t\t\t</screen>'
	skinHD = '\n\t\t\t<screen position="center,60" size="820,637" backgroundColor="#161616" title="OpenXTA Forum">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/XtrendHD.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,127" size="800,500" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="user" position="10,127" size="800,500" backgroundColor="#161616" foregroundColor="#FFFFFF" font="Regular;22" halign="left" zPosition="1" />\n\t\t\t</screen>'
	skinHDwhite = '\n\t\t\t<screen position="center,60" size="820,637" backgroundColor="#FFFFFF" title="OpenXTA Forum">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/XtrendHD_white.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,127" size="800,500" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="user" position="10,127" size="800,500" backgroundColor="#FFFFFF" foregroundColor="#FFFFFF" font="Regular;22" halign="left" zPosition="1" />\n\t\t\t</screen>'

	def __init__(self, session):
		self.colorfile = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/db/color')
		if fileExists(self.colorfile):
			f = open(self.colorfile, 'r')
			if 'white' in f:
				self.white = True
			else:
				self.white = False
			f.close()
		else:
			self.white = False
		deskWidth = getDesktop(0).size().width()
		if deskWidth == 1280 and self.white == False:
			self.skin = OpenXtaMain.skinHD
			self.xd = False
		elif deskWidth == 1280 and self.white == True:
			self.skin = OpenXtaMain.skinHDwhite
			self.xd = False
		elif deskWidth <= 1025 and self.white == False:
			self.skin = OpenXtaMain.skin
			self.xd = True
		elif deskWidth <= 1025 and self.white == True:
			self.skin = OpenXtaMain.skinwhite
			self.xd = True
		self.session = session
		Screen.__init__(self, session)
		self.baseurl = 'http://www.xtrend-alliance.com/'
		self.menuentries = []
		self.menulink = []
		self.menu = True
		self.hideflag = True
		self.ready = False
		self['menu'] = ItemList([])
		self['menu'].hide()
		self['user'] = ScrollLabel('')
		self['user'].hide()
		self['actions'] = ActionMap(['OkCancelActions',
		 'DirectionActions',
		 'ColorActions',
		 'MovieSelectionActions',
		 'HelpActions'], {'ok': self.ok,
		 'cancel': self.exit,
		 'down': self.down,
		 'up': self.up,
		 'right': self.rightDown,
		 'left': self.leftUp,
		 'red': self.red,
		 'yellow': self.yellow,
		 'green': self.green,
		 'blue': self.hideScreen,
		 'showEventInfo': self.showHelp,
		 'contextMenu': self.showHelp,
		 'displayHelp': self.infoScreen}, -1)
		self.makeMenuTimer = eTimer()
		self.makeMenuTimer.callback.append(self.download(self.baseurl, self.makeMenu))
		self.makeMenuTimer.start(500, True)

	def makeMenu(self, output):
		startpos1 = find(output, '<!-- ::: CONTENT ::: -->')
		if startpos1 == -1:
			self.session.open(MessageBox, 'Unknown content found', MessageBox.TYPE_INFO)
			self.close()

		else:
			endpos1 = find(output, '<!-- ::: FOOTER')
			bereich = output[startpos1:endpos1]
			bereich = transHTML(bereich)
			titel = re.findall('<td class=\'col_c_forum\'>\s*?<h4>\s*?<a href=".*?" title=\'.*?\'>(.*?)</a>', bereich)
			post = re.findall('<ul class=\'last_post ipsType_small\'>\s*?<li>\s*?<a href=\'.*?\' title=\'.*?\'>(.*?)</a>', bereich)
			date = re.findall('title=\'View last post\'>(.*?)</a>', bereich)
			user = re.findall('<li>By \n\t(.*?)\s*?</li>', bereich)
			link = re.findall('<td class=\'col_c_forum\'>\s*?<h4>\s*?<a href="(.*?)" title=', bereich)
			idx = 0
			for x in titel:
				idx += 1

			for i in range(idx):
				try:
					x = ''
					res = [x]
					if self.xd == True:
						if self.white == True:
							line = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/line_gray.png')
							if fileExists(line):
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(600, 1), png=loadPNG(line)))
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(600, 1), png=loadPNG(line)))
							res.append(MultiContentEntryText(pos=(0, 1), size=(45, 48), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=0, flags=RT_HALIGN_LEFT, text=''))
							res.append(MultiContentEntryText(pos=(45, 1), size=(555, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=titel[i]))
							res.append(MultiContentEntryText(pos=(45, 25), size=(340, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=post[i]))
							res.append(MultiContentEntryText(pos=(385, 25), size=(105, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=convertDate(date[i])))
							res.append(MultiContentEntryText(pos=(490, 25), size=(110, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=user[i]))
							if convertDate(date[i]) == 'Today':
								png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/forum_new-48.png')
								if fileExists(png):
									res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
							else:
								png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/forum_old-48.png')
								if fileExists(png):
									res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
						else:
							line = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/line_white.png')
							if fileExists(line):
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(600, 1), png=loadPNG(line)))
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(600, 1), png=loadPNG(line)))
							res.append(MultiContentEntryText(pos=(45, 1), size=(555, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=titel[i]))
							res.append(MultiContentEntryText(pos=(45, 25), size=(340, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=post[i]))
							res.append(MultiContentEntryText(pos=(385, 25), size=(105, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=convertDate(date[i])))
							res.append(MultiContentEntryText(pos=(490, 25), size=(110, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=user[i]))
							if convertDate(date[i]) == 'Today':
								png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/forum_new-48.png')
								if fileExists(png):
									res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
							else:
								png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/forum_old-48.png')
								if fileExists(png):
									res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
					elif self.white == True:
						line = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/line_gray.png')
						if fileExists(line):
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(800, 1), png=loadPNG(line)))
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(800, 1), png=loadPNG(line)))
						res.append(MultiContentEntryText(pos=(0, 1), size=(45, 48), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=0, flags=RT_HALIGN_LEFT, text=''))
						res.append(MultiContentEntryText(pos=(45, 1), size=(755, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=titel[i]))
						res.append(MultiContentEntryText(pos=(45, 25), size=(485, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=post[i]))
						res.append(MultiContentEntryText(pos=(530, 25), size=(120, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=convertDate(date[i])))
						res.append(MultiContentEntryText(pos=(650, 25), size=(150, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=user[i]))
						if convertDate(date[i]) == 'Today':
							png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/forum_new-48.png')
							if fileExists(png):
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
						else:
							png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/forum_old-48.png')
							if fileExists(png):
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
					else:
						line = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/line_white.png')
						if fileExists(line):
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(800, 1), png=loadPNG(line)))
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(800, 1), png=loadPNG(line)))
						res.append(MultiContentEntryText(pos=(45, 1), size=(755, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=titel[i]))
						res.append(MultiContentEntryText(pos=(45, 25), size=(485, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=post[i]))
						res.append(MultiContentEntryText(pos=(530, 25), size=(120, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=convertDate(date[i])))
						res.append(MultiContentEntryText(pos=(650, 25), size=(150, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=user[i]))
						if convertDate(date[i]) == 'Today':
							png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/forum_new-48.png')
							if fileExists(png):
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
						else:
							png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/forum_old-48.png')
							if fileExists(png):
								res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
					self.menulink.append(link[i])
					self.menuentries.append(res)
				except IndexError:
					pass

			self['menu'].l.setList(self.menuentries)
			self['menu'].l.setItemHeight(50)
			self['menu'].show()
			self.ready = True

	def ok(self):
		if self.ready == True:
			try:
				c = self.getIndex(self['menu'])
				link = self.menulink[c]
				self.session.openWithCallback(self.selectMenu, OpenXtaThread, link, False, False)
			except IndexError:
				pass

	def green(self):
		if self.ready == True:
			self.session.openWithCallback(self.selectMenu, OpenXtaThread, 'http://www.xtrend-alliance.com/index.php?app=core&module=search&do=viewNewContent&search_app=forums&change=1&period=week&userMode=&followedItemsOnly=0', False, True)

	def yellow(self):
		if self.ready == True:
			if self.white == False:
				self.session.openWithCallback(self.whitecolor, MessageBox, _('\nFarbe zu Weiss wechseln?'), MessageBox.TYPE_YESNO)
			elif self.white == True:
				self.session.openWithCallback(self.graycolor, MessageBox, _('\nFarbe zu Grau wechseln?'), MessageBox.TYPE_YESNO)

	def red(self):
		if self.ready == True:
			self.session.open(OpenXtaFav)

	def whitecolor(self, answer):
		if answer is True:
			if fileExists(self.colorfile):
				f = open(self.colorfile, 'w')
				f.write('white')
				f.close()
				self.container = eConsoleAppContainer()
				self.container.execute('cp -f ' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/plugin_white.png ') + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/plugin.png'))
				del self.container
				self.session.openWithCallback(self.redReturn, OpenXtaMain)

	def graycolor(self, answer):
		if answer is True:
			if fileExists(self.colorfile):
				f = open(self.colorfile, 'w')
				f.write('gray')
				f.close()
				self.container = eConsoleAppContainer()
				self.container.execute('cp -f ' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/plugin_gray.png ') + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/plugin.png'))
				del self.container
				self.session.openWithCallback(self.redReturn, OpenXtaMain)

	def redReturn(self):
		self.close()

	def showHelp(self):
		self.session.open(MessageBox, '\n%s' % 'Rot = Favoriten\nGelb = Farbe wechseln\nGr\xc3\xbcn = Die neusten Beitr\xc3\xa4ge\nHelp = Update Check', MessageBox.TYPE_INFO)

	def selectMenu(self):
		self['menu'].selectionEnabled(1)

	def getIndex(self, list):
		return list.getSelectedIndex()

	def down(self):
		if self.menu == True:
			self['menu'].down()
		else:
			self['user'].pageDown()

	def up(self):
		if self.menu == True:
			self['menu'].up()
		else:
			self['user'].pageUp()

	def rightDown(self):
		if self.menu == True:
			self['menu'].pageDown()
		else:
			self['user'].pageDown()

	def leftUp(self):
		if self.menu == True:
			self['menu'].pageUp()
		else:
			self['user'].pageUp()

	def download(self, link, name):
		getPage(link).addCallback(name).addErrback(self.downloadError)

	def downloadError(self, output):
		pass

	def infoScreen(self):
		self.session.open(infoOpenXta)

	def hideScreen(self):
		if self.hideflag == True:
			self.hideflag = False
			count = 40
			while count > 0:
				count -= 1
				f = open('/proc/stb/video/alpha', 'w')
				f.write('%i' % (config.av.osd_alpha.value * count / 40))
				f.close()

		else:
			self.hideflag = True
			count = 0
			while count < 40:
				count += 1
				f = open('/proc/stb/video/alpha', 'w')
				f.write('%i' % (config.av.osd_alpha.value * count / 40))
				f.close()

	def exit(self):
		if self.hideflag == False:
			f = open('/proc/stb/video/alpha', 'w')
			f.write('%i' % config.av.osd_alpha.value)
			f.close()
		if self.menu == False:
			self.menu = True
			self['user'].hide()
			self['menu'].show()
		else:
			self.close()


def main(session, **kwargs):
	session.open(OpenXtaMain)


def Plugins(**kwargs):
	return [PluginDescriptor(name='OpenXTA Reader', description='xtrend-alliance.com', where=[PluginDescriptor.WHERE_PLUGINMENU], icon='plugin.png', fnc=main), PluginDescriptor(name='OpenXTA Reader', description='xtrend-alliance.com', where=[PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main)]
