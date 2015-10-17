from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ScrollLabel import ScrollLabel
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap, NumberActionMap
from Components.config import config
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Tools.Directories import fileExists
from Plugins.Plugin import PluginDescriptor
from enigma import eListboxPythonMultiContent, eTimer, gFont, loadPNG, RT_HALIGN_LEFT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eEnv

import os
from twisted.web.client import getPage, downloadPage
from lxml import etree
from datetime import datetime, date, timedelta


def convertDate(datestr):
	if datestr == '':
		return ''
	d = datetime.strptime(datestr,'%Y-%m-%dT%H:%M:%SZ')
	if datetime.now().date() == d.date():
		return _('Today')
	elif (datetime.now() - timedelta(days=1)).date() == d.date():
		return _('Yesterday')
	return d.strftime('%d-%m-%y')


class OpenXtaScreen(Screen):

	def __init__(self, session):
		Screen.__init__(self, session)
		self.hideflag = True

	def download(self, link, name):
		getPage(link).addCallback(name).addErrback(self.downloadError)

	def downloadError(self, output):
		pass

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

	def showScreen(self):
		if self.hideflag == False:
			f = open('/proc/stb/video/alpha', 'w')
			f.write('%i' % config.av.osd_alpha.value)
			f.close()


class OpenXtaThread(OpenXtaScreen):
	skin = '\n\t\t\t<screen position="center,60" size="820,637" backgroundColor="#161616" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/XtrendHD.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,127" size="800,500" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t</screen>'

	def __init__(self, session, link):
		self.skin = OpenXtaThread.skin
		OpenXtaScreen.__init__(self, session)
		self.lastpage = True
		self.ready = False
		self.level = False
		self.currentpage = 1
		self.lastpage = 1
		self.threadtitle = ''
		self.link = link
		self.postlink = ''
		self.linkback = ''
		self.titlelist = []
		self.threadlink = []
		self.threadentries = []
		self['menu'] = ItemList([])
		self['menu'].hide()
		self["key_red"] = Label(_("Add to Favourites"))
		self["key_green"] = Label(_("Info"))
		self["key_yellow"] = Label(_("Info"))
		self["key_blue"] = Label(_("Hide"))
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
		 'red': self.red,
		 'blue': self.hideScreen,
		 'showEventInfo': self.showHelp,
		 'contextMenu': self.showHelp}, -1)
		self.makeThreadTimer = eTimer()
		self.makeThreadTimer.callback.append(self.download(self.link, self.makeThreadView))
		self.makeThreadTimer.start(500, True)

	def addTableEntry(self, title, stats, date, user, logo, link):
		x = ''
		res = [x]
		line = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/line_white.png')
		if fileExists(line):
			res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(800, 1), png=loadPNG(line)))
			res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(800, 1), png=loadPNG(line)))
		res.append(MultiContentEntryText(pos=(45, 1), size=(755, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=title))
		res.append(MultiContentEntryText(pos=(45, 25), size=(485, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=stats))
		res.append(MultiContentEntryText(pos=(530, 25), size=(120, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=convertDate(date)))
		res.append(MultiContentEntryText(pos=(650, 25), size=(150, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=user))
		if convertDate(date) == 'Today':
			png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/thread_new-30.png')
			if fileExists(png):
				res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
		else:
			png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/%s.png') % logo
			if fileExists(png):
				res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
		self.titlelist.append(title)
		self.threadlink.append(link)
		self.threadentries.append(res)

	def makeThreadView(self, output):
		try:
			parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True)
			htmltree = etree.fromstring(output, parser)

			title_element = htmltree.find('.//header[@class]/h1[@class]')
			title = etree.tostring(title_element, method='text').strip()
			page_element = htmltree.find('.//li[@class="ipsPagination_pageJump"]/a')
			if page_element is not None:
				pagestr = page_element.text.encode('utf8')
				splitted_pagestr = pagestr.split()
				title += ' | ' + _('Page %s of %s') % (splitted_pagestr[1], splitted_pagestr[3])
				self.lastpage = int(splitted_pagestr[3])

			for subforum in htmltree.findall('.//li[@data-forumid]'):
				subforum_title_element = subforum.find('.//h4[@class]/a')
				subforum_title = subforum_title_element.text.encode('utf8').strip()

				stats_element = subforum.find('.//div[@class="ipsDataItem_stats ipsDataItem_statsLarge"]')
				if len(stats_element):
					stats = _('Posts: ') + stats_element[0][0].text.strip()
				else:
					stats = _('No posts here yet')

				last_poster_element = subforum.find('.//ul[@class="ipsDataItem_lastPoster ipsDataItem_withPhoto"]')
				date_element = last_poster_element.find('.//time[@datetime]')
				if date_element is not None:
					date = date_element.get('datetime')
				else:
					date = ''

				if len(last_poster_element) > 1:
					user = last_poster_element[2][0].text.encode('utf8')
				else:
					user = ''

				logo = 'thread_old-30'

				link_element = subforum.find('.//h4[@class]/a')
				link = link_element.get('href')

				self.addTableEntry(subforum_title, stats, date, user, logo, link)

			for thread in htmltree.findall('.//li[@data-rowid]'):
				thread_title_element = thread.find('.//h4[@class]/a/span')
				thread_title = thread_title_element.text.encode('utf8').strip()

				stats_element = thread.find('.//ul[@class="ipsDataItem_stats"]')
				stats = _('Replies: ') + stats_element[0][0].text
				stats += ', ' + _('Views: ') + stats_element[1][0].text

				last_poster_element = thread.find('.//ul[@class="ipsDataItem_lastPoster ipsDataItem_withPhoto"]')
				date_element = last_poster_element.find('.//time[@datetime]')
				if date_element is not None:
					date = date_element.get('datetime')
				else:
					date = ''

				user = last_poster_element[1][0].text.encode('utf8')

				logo_element = thread.find('.//div[@class]/span/span[@title="Pinned"]')
				if logo_element is not None:
					logo = 'thread_sticky-30'
				else:
					logo = 'thread_old-30'

				link_element = thread.find('.//h4[@class]/a')
				link = link_element.get('href')

				self.addTableEntry(thread_title, stats, date, user, logo, link)

			self.threadtitle = title
			self.setTitle(title)

		except etree.Error as e:
			print 'OpenXtaReader Exception: ', e

		self['menu'].l.setList(self.threadentries)
		self['menu'].l.setItemHeight(50)
		self['menu'].moveToIndex(0)
		self['menu'].show()
		self.ready = True

	def ok(self):
		try:
			c = self['menu'].getSelectedIndex()
			self.postlink = self.threadlink[c]
			if 'index.php?/forum' in self.postlink:
				self.level = True
				self.titlelist = []
				self.threadlink = []
				self.threadentries = []
				self.linkback = self.link
				self.link = self.postlink
				self.download(self.link, self.makeThreadView)
			else:
				self.session.open(OpenXtaPost, self.postlink)
		except IndexError:
			pass

	def red(self):
		if self.ready == True:
			try:
				c = self['menu'].getSelectedIndex()
				name = self.titlelist[c]
				self.session.openWithCallback(self.red_return, MessageBox, _("\nAdd post '%s' to favorites?") % name, MessageBox.TYPE_YESNO)
			except IndexError:
				pass

	def red_return(self, answer):
		if answer is True:
			c = self['menu'].getSelectedIndex()
			favoriten = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/db/favoriten')
			if fileExists(favoriten):
				f = open(favoriten, 'a')
				data = self.titlelist[c] + ':::' + self.threadlink[c]
				f.write(data)
				f.write(os.linesep)
				f.close()
			self.session.open(OpenXtaFav)

	def nextPage(self):
		self.currentpage += 1
		if self.currentpage >= self.lastpage:
			self.currentpage = self.lastpage
		link = self.link + '/&page=' + str(self.currentpage)
		self.titlelist = []
		self.threadlink = []
		self.threadentries = []
		self['menu'].hide()
		self.makeThreadTimer.callback.append(self.download(link, self.makeThreadView))

	def prevPage(self):
		self.currentpage -= 1
		if self.currentpage == 0:
			self.currentpage = 1
		link = self.link + '/&page=' + str(self.currentpage)
		self.titlelist = []
		self.threadlink = []
		self.threadentries = []
		self['menu'].hide()
		self.makeThreadTimer.callback.append(self.download(link, self.makeThreadView))

	def gotoPage(self, number):
		self.session.openWithCallback(self.numberEntered, getNumber, number)

	def numberEntered(self, number):
		if number is None or number == 0:
			pass
		else:
			if int(number) > self.lastpage:
				number = self.lastpage
				if number > 1:
					self.session.open(MessageBox, _('\nOnly %s pages available. Goto page %s.') % (number, number), MessageBox.TYPE_INFO, timeout=3)
				else:
					self.session.open(MessageBox, _('\nOnly %s page available. Goto page %s.') % (number, number), MessageBox.TYPE_INFO, timeout=3)
			self.currentpage = int(number)
			link = self.link + '/&page=' + str(self.currentpage)
			self.titlelist = []
			self.threadlink = []
			self.threadentries = []
			self['menu'].hide()
			self.makeThreadTimer.callback.append(self.download(link, self.makeThreadView))

	def showHelp(self):
		self.session.open(MessageBox, '\n%s' % '0 - 999 = ' + _('Page') + '\nBouquet = +- ' + _('Page') +'\n' + _('Red') + ' = ' + _('Add to favorites'), MessageBox.TYPE_INFO)

	def selectMenu(self):
		self['menu'].selectionEnabled(1)

	def down(self):
		self['menu'].down()

	def up(self):
		self['menu'].up()

	def rightDown(self):
		self['menu'].pageDown()

	def leftUp(self):
		self['menu'].pageUp()

	def exit(self):
		self.showScreen()
		if self.level == True:
			self.link = self.linkback
			self.level = False
			self.titlelist = []
			self.threadlink = []
			self.threadentries = []
			self.download(self.link, self.makeThreadView)
		else:
			self.close()


class OpenXtaLatestPosts(OpenXtaScreen):
	skin = '\n\t\t\t<screen position="center,60" size="820,637" backgroundColor="#161616" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/XtrendHD.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,127" size="800,500" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t</screen>'

	def __init__(self, session, link):
		self.skin = OpenXtaThread.skin
		OpenXtaScreen.__init__(self, session)
		self.ready = False
		self.threadtitle = _('Latest Posts')
		self.titlelist = []
		self.threadlink = []
		self.threadentries = []
		self['menu'] = ItemList([])
		self['menu'].hide()
		self["key_red"] = Label(_("Add to Favourites"))
		self["key_green"] = Label(_("Info"))
		self["key_yellow"] = Label(_("Info"))
		self["key_blue"] = Label(_("Hide"))
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
		 'red': self.red,
		 'blue': self.hideScreen,
		 'showEventInfo': self.showHelp,
		 'contextMenu': self.showHelp}, -1)
		self.makeTimer = eTimer()
		self.makeTimer.callback.append(self.download(link, self.makeLatestPostsView))
		self.makeTimer.start(500, True)

	def addTableEntry(self, title, stats, date, user, logo, link):
		x = ''
		res = [x]
		line = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/line_white.png')
		if fileExists(line):
			res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(800, 1), png=loadPNG(line)))
			res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(800, 1), png=loadPNG(line)))
		res.append(MultiContentEntryText(pos=(45, 1), size=(755, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=title))
		res.append(MultiContentEntryText(pos=(45, 25), size=(485, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=stats))
		res.append(MultiContentEntryText(pos=(530, 25), size=(120, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=convertDate(date)))
		res.append(MultiContentEntryText(pos=(650, 25), size=(150, 24), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=user))
		if convertDate(date) == 'Today':
			png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/thread_new-30.png')
			if fileExists(png):
				res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
		else:
			png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/%s.png') % logo
			if fileExists(png):
				res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
		self.titlelist.append(title)
		self.threadlink.append(link)
		self.threadentries.append(res)

	def makeLatestPostsView(self, output):
		try:
			parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True)
			htmltree = etree.fromstring(output, parser)

			for thread in htmltree.findall('.//li[@class="ipsDataItem ipsDataItem_responsivePhoto   "]'):
				thread_title_element = thread.find('.//h4[@class]/a')
				thread_title = thread_title_element.text.encode('utf8').strip()

				stats_element = thread.find('.//ul[@class="ipsDataItem_stats"]')
				stats = _('Replies: ') + stats_element[0][0].text
				stats += ', ' + _('Views: ') + stats_element[1][0].text

				last_poster_element = thread.find('.//ul[@class="ipsDataItem_lastPoster ipsDataItem_withPhoto"]')
				date_element = last_poster_element.find('.//time[@datetime]')
				if date_element is not None:
					date = date_element.get('datetime')
				else:
					date = ''

				user = last_poster_element[1][0].text.encode('utf8')

				logo_element = thread.find('.//div[@class]/span/span[@title="Pinned"]')
				if logo_element is not None:
					logo = 'thread_sticky-30'
				else:
					logo = 'thread_old-30'

				link_element = thread.find('.//h4[@class]/a')
				link = link_element.get('href')

				self.addTableEntry(thread_title, stats, date, user, logo, link)

			self.setTitle(self.threadtitle)

		except etree.Error as e:
			print 'OpenXtaReader Exception: ', e

		self['menu'].l.setList(self.threadentries)
		self['menu'].l.setItemHeight(50)
		self['menu'].moveToIndex(0)
		self['menu'].show()
		self.ready = True

	def ok(self):
		try:
			c = self['menu'].getSelectedIndex()
			link = self.threadlink[c]
			if 'index.php?/forum' in link:
				self.session.open(OpenXtaThread, link)
			else:
				self.session.open(OpenXtaPost, link)
		except IndexError:
			pass

	def red(self):
		if self.ready == True:
			try:
				c = self['menu'].getSelectedIndex()
				name = self.titlelist[c]
				self.session.openWithCallback(self.red_return, MessageBox, _("\nAdd post '%s' to favorites?") % name, MessageBox.TYPE_YESNO)
			except IndexError:
				pass

	def red_return(self, answer):
		if answer is True:
			c = self['menu'].getSelectedIndex()
			favoriten = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/db/favoriten')
			if fileExists(favoriten):
				f = open(favoriten, 'a')
				data = self.titlelist[c] + ':::' + self.threadlink[c]
				f.write(data)
				f.write(os.linesep)
				f.close()
			self.session.open(OpenXtaFav)

	def showHelp(self):
		self.session.open(MessageBox, '\n%s' % '0 - 999 = ' + _('Page') + '\nBouquet = +- ' + _('Page') +'\n' + _('Red') + ' = ' + _('Add to favorites'), MessageBox.TYPE_INFO)

	def selectMenu(self):
		self['menu'].selectionEnabled(1)

	def down(self):
		self['menu'].down()

	def up(self):
		self['menu'].up()

	def rightDown(self):
		self['menu'].pageDown()

	def leftUp(self):
		self['menu'].pageUp()

	def exit(self):
		self.showScreen()
		self.close()


class OpenXtaPost(OpenXtaScreen):
	skin = '\n\t\t\t<screen position="center,60" size="820,637" backgroundColor="#161616" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/XtrendHD.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="textpage" position="10,127" size="800,500" backgroundColor="#161616" foregroundColor="#FFFFFF" font="Regular;22" halign="left" zPosition="1" />\n\t\t\t</screen>'

	def __init__(self, session, link):
		self.skin = OpenXtaPost.skin
		OpenXtaScreen.__init__(self, session)
		self.ready = False
		self.currentpage = 1
		self.lastpage = 1
		self.link = link
		self.gotoLastPost = True
		self['textpage'] = ScrollLabel('')
		self["key_red"] = Label(_("Add to Favourites"))
		self["key_green"] = Label(_("Info"))
		self["key_yellow"] = Label(_("Info"))
		self["key_blue"] = Label(_("Hide"))
		self['NumberActions'] = NumberActionMap(['NumberActions',
		 'OkCancelActions',
		 'DirectionActions',
		 'ColorActions',
		 'ChannelSelectBaseActions',
		 'MovieSelectionActions',
		 'HelpActions'], {
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
		 'red': self.red,
		 'blue': self.hideScreen,
		 'showEventInfo': self.showHelp,
		 'contextMenu': self.showHelp}, -1)
		self.makePostTimer = eTimer()
		self.makePostTimer.callback.append(self.download(link, self.gotoLastPage))
		self.makePostTimer.start(500, True)

	def makePostView(self, output):
		try:
			text = ''
			parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True)
			htmltree = etree.fromstring(output, parser)

			title_element = htmltree.find('.//h1[@class="ipsType_pageTitle"]')
			title = title_element.text.strip().encode('utf8')
			title = title[0:45] + '... | ' + _('Page %i of %i') % (self.currentpage, self.lastpage)
			self.setTitle(title)

			for post in htmltree.findall('.//article[@itemscope]'):
				author_element = post.find('.//h3[@itemprop="creator"]/strong[@itemprop]/a')
				author = author_element.text.strip().encode('utf8')
				text += _('Author: ') + author

				date_element = post.find('.//div[@data-commentid]/div/p/time')
				date = date_element.get('datetime')
				text += '  ' + _('Date: ') + convertDate(date) + '\n\n'

				comment_element = post.find('.//div[@data-commentid]/div/div[@data-role="commentContent"]')
				comment = etree.tostring(comment_element, method = 'text', encoding = 'utf8').strip()
				comment += '\n===========================================================\n'

				text += comment

			self['textpage'].setText(text)
			self['textpage'].show()
			if self.gotoLastPost:
				self['textpage'].lastPage()
				self.gotoLastPost = False

		except etree.Error as e:
			print 'OpenXtaReader Exception: ', e

		self.ready = True

	def red(self):
		if self.ready == True:
			try:
				c = self['menu'].getSelectedIndex()
				name = self.titlelist[c]
				self.session.openWithCallback(self.red_return, MessageBox, _("\nAdd post '%s' to favorites?") % name, MessageBox.TYPE_YESNO)
			except IndexError:
				pass

	def red_return(self, answer):
		if answer is True:
			c = self['menu'].getSelectedIndex()
			favoriten = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/db/favoriten')
			if fileExists(favoriten):
				f = open(favoriten, 'a')
				data = self.titlelist[c] + ':::' + self.threadlink[c]
				f.write(data)
				f.write(os.linesep)
				f.close()
			self.session.open(OpenXtaFav)

	def gotoLastPage(self, output):
		try:
			parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True)
			htmltree = etree.fromstring(output, parser)

			self.gotoLastPost = True
			page_element = htmltree.find('.//li[@class="ipsPagination_pageJump"]/a')
			if page_element is not None:
				pagestr = page_element.text.encode('utf8')
				splitted_pagestr = pagestr.split()
				self.lastpage = int(splitted_pagestr[3])
				self.currentpage = self.lastpage
				self.download(self.link + '&page=' + str(self.lastpage), self.makePostView)
			else:
				self.makePostView(output)

		except etree.Error as e:
			print 'OpenXtaReader Exception: ', e

	def nextPage(self):
		self.gotoLastPost = False
		self.currentpage += 1
		if self.currentpage >= self.lastpage:
			self.currentpage = self.lastpage
		link = self.link + '&page=' + str(self.currentpage)
		self.makePostTimer.callback.append(self.download(link, self.makePostView))

	def prevPage(self):
		self.gotoLastPost = False
		self.currentpage -= 1
		if self.currentpage == 0:
			self.currentpage = 1
		link = self.link + '&page=' + str(self.currentpage)
		self.makePostTimer.callback.append(self.download(link, self.makePostView))

	def gotoPage(self, number):
		self.session.openWithCallback(self.numberEntered, getNumber, number)

	def numberEntered(self, number):
		if number is None or number == 0:
			pass
		else:
			if int(number) > self.lastpage:
				number = self.lastpage
				if number > 1:
					self.session.open(MessageBox, _('\nOnly %s pages available. Goto page %s.') % (number, number), MessageBox.TYPE_INFO, timeout=3)
				else:
					self.session.open(MessageBox, _('\nOnly %s page available. Goto page %s.') % (number, number), MessageBox.TYPE_INFO, timeout=3)
			self.gotoLastPost = False
			self.currentpage = int(number)
			link = self.link + '&page=' + str(self.currentpage)
			self.makePostTimer.callback.append(self.download(link, self.makePostView))

	def showHelp(self):
		self.session.open(MessageBox, '\n%s' % '0 - 999 = ' + _('Page') + '\nBouquet = +- ' + _('Page') +'\n' + _('Red') + ' = ' + _('Add to favorites'), MessageBox.TYPE_INFO)

	def down(self):
		self['textpage'].pageDown()

	def up(self):
		self['textpage'].pageUp()

	def rightDown(self):
		self['textpage'].pageDown()

	def leftUp(self):
		self['textpage'].pageUp()

	def exit(self):
		self.showScreen()
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


class OpenXtaFav(OpenXtaScreen):
	skin = '\n\t\t\t<screen position="center,60" size="820,637" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/XtrendHD.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="label" position="343,127" size="250,22" font="Regular;18" foregroundColor="#FFFFFF" backgroundColor="#000000" halign="left" transparent="1" zPosition="2" />\n\t\t\t\t<ePixmap position="319,127" size="18,65" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/buttons/red.png') + '" alphatest="blend" zPosition="2" />\n\t\t\t\t<widget name="favmenu" position="10,157" size="800,475" scrollbarMode="showOnDemand" zPosition="1" />\n\t\t\t</screen>'

	def __init__(self, session):
		self.skin = OpenXtaFav.skin
		self.session = session
		OpenXtaScreen.__init__(self, session)
		self.favlist = []
		self.favlink = []
		self.count = 0
		self['favmenu'] = MenuList([])
		self['label'] = Label('= ' + _('Delete favorite'))
		self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions'], {'ok': self.ok,
		 'cancel': self.exit,
		 'down': self.down,
		 'up': self.up,
		 'red': self.red,
		 'blue': self.hideScreen}, -1)
		self.makeFav()

	def makeFav(self):
		self.setTitle('OpenXTA:::' + _('Favorites'))
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
			if 'index.php?/forum' in link:
				self.session.openWithCallback(self.exit, OpenXtaThread, link)
			else:
				self.session.openWithCallback(self.exit, OpenXtaPost, link)
		except IndexError:
			pass

	def red(self):
		if len(self.favlist) > 0:
			try:
				c = self.getIndex(self['favmenu'])
				name = self.favlist[c]
			except IndexError:
				name = ''

			self.session.openWithCallback(self.red_return, MessageBox, '\n' + _("Delete post '%s' from favorites?") % name, MessageBox.TYPE_YESNO)

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

	def exit(self):
		self.showScreen()
		self.close()


class ItemList(MenuList):

	def __init__(self, items, enableWrapAround = True):
		MenuList.__init__(self, items, enableWrapAround, eListboxPythonMultiContent)
		self.l.setFont(-1, gFont('Regular', 22))
		self.l.setFont(0, gFont('Regular', 20))
		self.l.setFont(1, gFont('Regular', 18))
		self.l.setFont(2, gFont('Regular', 16))


class OpenXtaMain(OpenXtaScreen):
	skin = '\n\t\t\t<screen position="center,60" size="820,637" backgroundColor="#161616" title="OpenXTA Forum">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="' + eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/XtrendHD.png') + '" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,127" size="800,500" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t</screen>'

	def __init__(self, session):
		self.skin = OpenXtaMain.skin
		self.session = session
		OpenXtaScreen.__init__(self, session)
		self.baseurl = 'http://www.xtrend-alliance.com/'
		self.menuentries = []
		self.menulink = []
		self.ready = False
		self['menu'] = ItemList([])
		self['menu'].hide()
		self["key_red"] = Label(_("Favourites"))
		self["key_green"] = Label(_("Latest Posts"))
		self["key_blue"] = Label(_("Hide"))
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
		 'green': self.green,
		 'blue': self.hideScreen,
		 'showEventInfo': self.showHelp,
		 'contextMenu': self.showHelp}, -1)
		self.makeMenuTimer = eTimer()
		self.makeMenuTimer.callback.append(self.download(self.baseurl, self.makeMenu))
		self.makeMenuTimer.start(500, True)

	def makeMenu(self, output):
		try:
			parser = etree.HTMLParser(remove_blank_text=True, remove_comments=True)
			htmltree = etree.fromstring(output, parser)

			for forum in htmltree.findall('.//li[@data-categoryid]'):
				#forum_title_element = forum.find('.//h2[@class="ipsType_sectionTitle ipsType_reset ipsType_blendLinks cForumTitle"]')
				#forum_title = etree.tostring(forum_title_element, method='text').strip()

				for subforum in forum.findall('.//li[@data-forumid]'):
					subforum_element = subforum.find('.//h4[@class="ipsDataItem_title ipsType_large"]')
					subforum_title = etree.tostring(subforum_element, method='text').strip()
					link = subforum_element[0].get('href')

					last_post_element = subforum.find('.//ul[@class]/li/a[@class="ipsType_break ipsContained"]')
					if last_post_element is not None:
						last_post_title = last_post_element.get('title').encode('utf8')
					else:
						last_post_title = _('No posts here yet')

					date_element = subforum.find('.//time[@datetime]')
					if last_post_element is not None:
						date = date_element.get('datetime')
					else:
						date = ''

					user_element = subforum.find('.//ul[@class]/li/a[@data-ipsHover]')
					if user_element is not None:
						user = etree.tostring(user_element, method='text').strip()
					else:
						user = ''

					x = ''
					res = [x]
					line = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/line_white.png')
					if fileExists(line):
						res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(600, 1), png=loadPNG(line)))
						res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(600, 1), png=loadPNG(line)))
					res.append(MultiContentEntryText(pos=(45, 1), size=(555, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=subforum_title))
					res.append(MultiContentEntryText(pos=(45, 25), size=(340, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=last_post_title))
					res.append(MultiContentEntryText(pos=(385, 25), size=(105, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=convertDate(date)))
					res.append(MultiContentEntryText(pos=(490, 25), size=(110, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=user))
					if convertDate(date) == 'Today':
						png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/forum_new-48.png')
						if fileExists(png):
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
					else:
						png = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenXtaReader/pic/forum_old-48.png')
						if fileExists(png):
							res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 2), size=(44, 44), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))

					self.menulink.append(link)
					self.menuentries.append(res)

		except etree.Error as e:
			print 'OpenXtaReader Exception: ', e

		self['menu'].l.setList(self.menuentries)
		self['menu'].l.setItemHeight(50)
		self['menu'].show()
		self.ready = True

	def ok(self):
		if self.ready == True:
			try:
				c = self.getIndex(self['menu'])
				link = self.menulink[c]
				self.session.openWithCallback(self.selectMenu, OpenXtaThread, link)
			except IndexError:
				pass

	def green(self):
		if self.ready == True:
			self.session.openWithCallback(self.selectMenu, OpenXtaLatestPosts, 'http://www.xtrend-alliance.com/index.php?/activity/&type=forums_topic&change_section=1')

	def red(self):
		if self.ready == True:
			self.session.open(OpenXtaFav)

	def redReturn(self):
		self.close()

	def showHelp(self):
		self.session.open(MessageBox, '\n%s' % _('Red') + ' = ' + _('Favorites') + '\n' + _('Green = Latest posts'), MessageBox.TYPE_INFO)

	def selectMenu(self):
		self['menu'].selectionEnabled(1)

	def getIndex(self, list):
		return list.getSelectedIndex()

	def down(self):
		self['menu'].down()

	def up(self):
		self['menu'].up()

	def rightDown(self):
		self['menu'].pageDown()

	def leftUp(self):
		self['menu'].pageUp()

	def exit(self):
		self.showScreen()
		self.close()


def main(session, **kwargs):
	session.open(OpenXtaMain)


def Plugins(**kwargs):
	return [PluginDescriptor(name='OpenXTA Reader', description='xtrend-alliance.com', where=[PluginDescriptor.WHERE_PLUGINMENU], icon='plugin.png', fnc=main), PluginDescriptor(name='OpenXTA Reader', description='xtrend-alliance.com', where=[PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main)]
