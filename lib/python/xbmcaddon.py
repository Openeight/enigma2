import os, os.path, sys
import xml.etree.cElementTree 
# xbmc/interfaces/python/xbmcmodule/PythonAddon.cpp
# (with a little help from xbmcswift)

scripts = "/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/XBMC"
for name in os.listdir(scripts):
       if "script." in name:
                      fold = scripts + "/" + name + "/lib"
                      sys.path.append(fold)

class Addon:

	def __init__(self, id=None):
		self.id = id

	def getLocalizedString(self, idx=" "):
             path = self.getAddonInfo("path")             
             xfile = path + "/resources/language/English/strings.xml"
             tree = xml.etree.cElementTree.parse(xfile)
             root = tree.getroot()
             for string in root.iter('string'):
                        id = string.get('id')
                        text = string.text
                        if int(id) == int(idx):
                              xtxt = text
                              return xtxt


	def getSetting(self,id=None):
	     item = id
             path = self.getAddonInfo("path")             
             xfile = path + "/resources/settings.xml" 
             f = open(xfile, 'r')
             xfile2 = f.read()
             f.close()
             if "&" in xfile2:
                    xfile2 = xfile2.replace("&", "AxNxD") 
                    f2 = open('/tmp/temp.xml', 'w')
                    f2.write(xfile2)
                    f2.close()
                    cmd = "mv '/tmp/temp.xml' " + xfile
                    os.system(cmd)                   
             tree = xml.etree.cElementTree.parse(xfile)
             root = tree.getroot() 
             for setting in root.iter('setting'):
                    type = setting.get('type')
                    if type == "bool":
                            idx = setting.get('id')
                            default = setting.get('default')
                            if idx == item:
                                   xtxt = default
                                   return xtxt

                    elif type == "action":
                            idx = setting.get('label')
                            action = setting.get('action')
                            if idx == item:
                                   xtxt = action
                                   return xtxt

                    elif type == "text":
                            idx = setting.get('id')
                            default = setting.get('default')
                            if idx == item:
                                   xtxt = default
                                   return xtxt

                    elif type == "enum":
                            idx = setting.get('id')
                            default = setting.get('default')
                            if idx == item:
                                   ix = default
                                   return int(ix)
                    elif type == "folder":
                            idx = setting.get('id')
                            default = setting.get('default')
                            if idx == item:
                                   xtxt = default
                                   return xtxt  
                    elif type == "labelenum":
                            idx = setting.get('id')
                            values = setting.get('values')
                            if idx == item:
                                   vals = values.split("|")
                                   n = len(vals)-1
                                   xtxt = vals[n]
                                   return xtxt               
                                                

	def setSetting(self, id, value):
        	"""Sets a script setting."""
		print "*** setSetting *** %s=%s" % (id, value)

	# sometimes called with an arg, e.g veehd
	def openSettings(self, arg=None):
		"""Opens this scripts self.settings dialog."""
		print "*** openSettings ***"

	def getAddonInfo(self, item):
                myfile = file(r"/etc/xbmc.txt")       
                icount = 0
                for line in myfile.readlines():
                       cachefold = line
                       break

                path = '/usr/lib/enigma2/python/Plugins/Extensions/XBMCAddons/XBMC/' + str(self.id)
                profile = cachefold + '/xbmc/profile/addon_data/' + str(self.id)
                cmd = "mkdir -p " + profile
                os.system(cmd)

                xfile = path + "/addon.xml"
#                print "get_version xfile =", xfile 
                tree = xml.etree.cElementTree.parse(xfile)
                root = tree.getroot()
                version = str(root.get('version'))
#                print "get_version version =", version    
                author = str(root.get('provider-name'))
                name = str(root.get('name'))
                id = str(root.get('id'))
                if item == "path":
                        return path
                elif item == "version":
                        return version
                elif item == "author":
                        return author
                elif item == "name":
                        return name
                elif item == "id":
                        return id
                elif item == "profile":
                        return profile        
                else:
                        return " "




























