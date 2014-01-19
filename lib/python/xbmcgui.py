#import xbmcinit
import os, sys
scripts = "/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/XBMC"

for name in os.listdir(scripts):
       if "script." in name:
                      fold = scripts + "/" + name + "/lib"
                      sys.path.append(fold)

def getCurrentWindowId():
	"""Returns the id for the current 'active' window as an integer."""
	return 0

def getCurrentWindowDialogId():
	"""Returns the id for the current 'active' dialog as an integer."""
	return 0

# xbmc/guilib/GUIListItem.h
ICON_OVERLAY_NONE = 0
ICON_OVERLAY_RAR = 1
ICON_OVERLAY_ZIP = 2
ICON_OVERLAY_LOCKED = 3
ICON_OVERLAY_HAS_TRAINER = 4
ICON_OVERLAY_TRAINED = 5
ICON_OVERLAY_UNWATCHED = 6
ICON_OVERLAY_WATCHED = 7
ICON_OVERLAY_HD = 8

class mock(object):
	'''
	A shapeless self-referring class that never raises
	an AttributeError, is always callable and will always
	evaluate as a string, int, float, bool, or container.
	'''
	# http://www.rafekettler.com/magicmethods.html
	def __new__(cls, *args): return object.__new__(cls)
	def __init__(self, *args): pass
	def __getattr__(self, name): return self
	def __call__(self, *args, **kwargs): return self
	def __int__(self): return 0
	def __float__(self): return 0
	def __str__(self): return '0'
	def __nonzero__(self): return False
	def __getitem__(self, key): return self
	def __setitem__(self, key,value): pass
	def __delitem__(self, key): pass
	def __len__(self): return 3
	def __iter__(self): return iter([self,self,self])

DialogProgress = mock()

Window = \
WindowDialog = \
WindowXML = \
WindowXMLDialog = mock()

Window.getResolution = lambda:5 # NTSC 16:9 (720x480)
Window.getWidth = lambda:720
Window.getHeight = lambda:480

Control = \
ControlButton = \
ControlCheckMark = \
ControlFadeLabel = \
ControlGroup = \
ControlImage = \
ControlLabel = \
ControlList = \
ControlProgress = \
ControlRadioButton = \
ControlTextBox = mock()     

def Log(text):
              file = open("/tmp/xbmclog.txt", "a")
              text = text + "\n"
              file.write(text)
              file.close()              
# xbmc/interfaces/python/xbmcmodule/listitem.cpp
class ListItem:
#def ListItem(name, iconImage, thumbnailImage):
#    def __init__(self, name, iconImage, thumbnailImage, path):

        def __init__(self, label=" ", label2=" ", iconImage=None, thumbnailImage="DefaultFolder.png", path="path"):
              if os.path.exists("/etc/debugxb"):
                  try:
                      print "ListItem label =", label
#                      Log("Blabel =%sthumbnailImage =%s" % (label, thumbnailImage))
                      print "ListItem label2 =", label2
#                      Log("Clabel =%sthumbnailImage =%s" % (label, thumbnailImage))
                      print "ListItem iconImage =", iconImage
#                      Log("Dlabel =%sthumbnailImage =%s" % (label, thumbnailImage))
                      print "ListItem thumbnailImage =", thumbnailImage
#                      Log("Elabel =%sthumbnailImage =%s" % (label, thumbnailImage))
                      print "ListItem path =", path
#                      Log("F label =%sthumbnailImage =%s" % (label, thumbnailImage))
                  except:    
                      pass
              if (".jpg" not in thumbnailImage) and (".png" not in thumbnailImage):
                      thumbnailImage = "DefaultFolder.png"
              
              
              if label is not None:
                      label = label.replace(" ", "-")
                      label = label.replace("&", "AxNxD")
                      label = label.replace("=", "ExQ")
              if path is not None:
                      if '|' in path:
		              path,headers = path.split('|')
#                      path = path.replace(" ", "-")
                      path = path.replace("&", "AxNxD")
                      path = path.replace("=", "ExQ")        
              if (path != "path"):
                      data = "name=" + str(path) + "&thumbnailImage=" + str(thumbnailImage)
              else:
                      data = "name=" + str(label) + "&thumbnailImage=" + str(thumbnailImage)
              try:
                      print "data =", data
              except:        
                      pass
              file = open("/tmp/data.txt", "a")
              file.write(data)
              file.close()


	def getLabel(self):
		"""Returns the listitem label."""
		return self.__dict__['label']

	def getLabel2(self):
		"""Returns the listitem's second label."""
		return self.__dict__['label2']

	def setLabel(self, label):
		"""Sets the listitem's label."""
		self.__dict__['label'] = label

	def setLabel2(self, label2):
		"""Sets the listitem's second label."""
		self.__dict__['label2'] = label2

	def setIconImage(self, icon):
		"""Sets the listitem's icon image."""
		self.__dict__['iconImage'] = icon

	def setThumbnailImage(self, thumb):
		"""Sets the listitem's thumbnail image."""
		self.__dict__['thumbnailImage'] = thumb

	def select(self, selected):
		"""Sets the listitem's selected status."""
		pass

	def isSelected(self):
		"""Returns the listitem's selected status."""
		return False

	def setInfo(self, type, infoLabels):
	     if os.path.exists("/etc/debugxb"):
	        try:
                    print "In listItem type =", type
                    print "In listItem infoLabels =", infoLabels
                except:    
                    pass
             file = open("/tmp/type.txt", "a")
             data = type
#             print "data : type =", data
             file.write(data)
             file.close()


	def setProperty(self, x1, x2):
             data = "&isPlayable=" + x1 + "&True/False=" + x2
             file = open("/tmp/data.txt", "a")
             file.write(data)
             file.close()
#             return


	def getProperty(self, key):
		"""Returns a listitem property as a string, similar to an infolabel."""
		return (self.__dict__[key] if key in self.__dict__ else None)

	def addContextMenuItems(self, items, replaceItems=None):
		"""Adds item to the context menu for media lists."""
		pass

	def setPath(self, path):
		"""Sets the listitem's path."""
		self.__dict__['path'] = path

# xbmc/interfaces/python/xbmcmodule/dialog.cpp
class Dialog:

	def ok(self, heading, line1, line2=None, line3=None):
		"""Show a dialog 'OK'."""
		print "*** dialog OK ***\n%s" % [heading, line1, line2, line3]
		return True

	def browse(self, type, heading, shares, mask=None, useThumbs=None, treatAsFolder=None, default=None, enableMultiple=None):
		"""Show a 'Browse' dialog."""
		print "*** dialog browse ***\n%s" % [heading, shares, default]
		return default

	def numeric(self, type, heading, default=0):
		"""Show a 'Numeric' dialog."""
		return self.choose('numeric', heading, [], default)

	def yesno(self, heading, line1, line2=None, line3=None, nolabel='no', yeslabel='yes'):
		"""Show a dialog 'YES/NO'."""
		query = '%s%s%s%s' % (heading or '', line1 or '', line2 or '', line3 or '')
		sel = self.choose('YES/NO', query, [yeslabel, nolabel])
		return (True if sel == 0 else False)

	def select(self, heading, list, autoclose=None):
		"""Show a select dialog."""
		return self.choose('select', heading, list)

	def chooseX(self, type, query, list, default=0):
		try: _dialogs
		except: xbmcinit.read_dialogs()
		dlg = '%s %s %s' % (repr(query), list, _mainid)
		sel = (_dialogs[dlg] if dlg in _dialogs else default)
		print "*** dialog %s ***\n%s <<< %s" % (type, sel, dlg)
		return sel

	def choose(self, type, query, list, default=0):
	        pass
# mock everything else, mostly


#class DialogProgress:

#	def create(self, heading, line1=None, line2=None, line3=None):
#		"""Create and show a progress dialog."""
#		pass

#	def update(self, percent, line1=None, line2=None, line3=None):
#		"""Update's the progress dialog."""
#		pass

#	def iscanceled(self):
#		"""Returns True if the user pressed cancel."""
#		return False

#	def close(self):
#		"""Close the progress dialog."""
#		pass

#class Window:

#	def __init__(self, windowId):
#		self.properties = {}
#		self.properties['windowId'] = windowId;

#	def addControl(self, control):
#		"""Add a Control to this window."""
#		pass

#	def addControls(self, controlList):
#		"""Add a list of Controls to this window."""
#		pass

#	def clearProperties(self):
#		"""Clears all window properties."""
#		self.properties = {}

#	def clearProperty(self, key):
#		"""Clears the specific window property."""
#		self.properties[key] = None

#	def close(self):
#		"""Closes this window."""
#		pass

#	def doModal(self):
#		"""Display this window until close() is called."""
#		pass

#	def getControl(self, controlId):
#		"""Get's the control from this window."""
#		pass

#	def getFocus(self, control):
#		"""returns the control which is focused."""
#		pass

#	def getFocusId(self):
#		"""returns the id of the control which is focused."""
#		return 0

#	def getHeight(self):
#		"""Returns the height of this screen."""
#		return 480

#	def getProperty(self, key):
#		"""Returns a window property as a string, similar to an infolabel."""
#		return self.properties[key] if key in self.properties else ''

#	def getResolution(self):
#		"""Returns the resolution of the screen. The returned value is one of the following:"""
#		return 5 # NTSC 16:9 (720x480)

#	def getWidth(self):
#		"""Returns the width of this screen."""
#		return 720

#	def onAction(self, action):
#		"""onAction method."""
#		pass

#	def onClick(self, control):
#		"""onClick method."""
#		pass

#	def onFocus(self, control):
#		"""onFocus method."""
#		pass

#	def onInit(self):
#		"""onInit method."""
#		pass

#	def removeControl(self, control):
#		"""Removes the control from this window."""
#		pass

#	def removeControls(self, controlList):
#		"""Removes a list of controls from this window."""
#		pass

#	def setCoordinateResolution(self, resolution):
#		"""Sets the resolution"""
#		pass

#	def setFocus(self, control):
#		"""Give the supplied control focus."""
#		pass

#	def setFocusId(self):
#		"""Gives the control with the supplied focus."""
#		pass

#	def setProperty(self, key, value):
#		"""Sets a window property, similar to an infolabel."""
#		self.properties[key] = value;

#	def show(self):
#		"""Show this window."""
#		pass

#class WindowDialog(Window):

#	def __init__(self):
#		Window.__init__(self, 0)
#		pass

#class WindowXML(Window):

#	def __init__(self, xmlFilename, scriptPath=None, defaultSkin=None, forceFallback=False):
#		Window.__init__(self, 0)

#	def addItem(item, position=None):
#		"""addItem(item[, position]) -- Add a new item to this Window List."""
#		pass

#	def clearList():
#		"""clearList() -- Clear the Window List."""
#		pass

#	def getCurrentListPosition():
#		"""getCurrentListPosition() -- Gets the current position in the Window List."""
#		return 0

#	def getListItem(position):
#		"""getListItem(position) -- Returns a given ListItem in this Window List."""
#		return None

#	def getListSize():
#		"""getListSize() -- Returns the number of items in this Window List."""
#		return 0

#	def removeItem(position):
#		"""removeItem(position) -- Removes a specified item based on position, from the Window List."""
#		pass

#	def setCurrentListPosition(position):
#		"""setCurrentListPosition(position) -- Set the current position in the Window List."""
#		return 0

## xbmc/interfaces/python/xbmcmodule/winxmldialog.cpp
#class WindowXMLDialog(WindowXML):

#	def __init__(self, xmlFilename, scriptPath=None, defaultSkin=None, defaultRes=None):
#		"""Create a new WindowXMLDialog script."""
#		WindowXML.__init__(self, xmlFilename, scriptPath, defaultSkin)








































