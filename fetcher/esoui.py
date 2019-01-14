import fetcher
import pycurl
import os
import zipfile
import logging
import shutil

from cStringIO import StringIO
from lxml import etree

class EsouiPluginSource(fetcher.PluginSource):
    name = "esoui"

    def __init__(self):
        self.log = logging.getLogger("EsouiPluginSource")
        
    def newItem(self):
        return EsouiItem()

    def fetchMetaData(self, item):
        url = "https://www.esoui.com/downloads/info%s.html" % (item.id)
        self.log.info("fetching %s" % (url))

        buffer = StringIO()
        response = self.__performGet(url, buffer)
        self.log.info("response was %s" % (response))
        buffer.reset()
        tree = etree.parse(buffer, etree.HTMLParser())
        metadata = {}
        metadata["title"] = tree.xpath("//div[@class = 'title']")[0].text.strip()
        metadata["version"] = tree.xpath("//div[@id = 'version']") [0].text.split(": ")[1].strip()
        metadata["updated"] = tree.xpath("//div[@id = 'safe']")[0].text.split(": ")[1].strip()
        metadata["id"] = item.id
        metadata["source"] = item.source
        metaItem = self.newItem()
        metaItem.load(metadata)
        return metaItem

    def fetchPlugin(self, item):
        url =  "https://cdn.esoui.com/downloads/file%s/" % (item.id)
        self.log.info("fetching %s" % (url))
        
        buffer = StringIO()
        response = self.__performGet(url, buffer)
        self.log.info("response was %s" % (response))
        return EsouiBinary(buffer, item)
        
    def __performGet(self, url, buffer):
        c = pycurl.Curl()
        c.setopt(c.URL, url)
        c.setopt(c.WRITEDATA, buffer)
        # c.setopt(c.HEADERFUNCTION, self.__header)
        c.setopt(c.HTTPHEADER, ["User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0", ])
        c.perform()
        response = c.getinfo(c.HTTP_CODE)
        c.close()
        return response
            
    def __header(self, data):
        self.log.debug("header: %s" % (data.strip()))

class EsouiItem(fetcher.PluginItem):
    def __init__(self):
        self.id = None
        self.title = None
        self.version = None
        self.updated = None
        self.path = None

class EsouiBinary(fetcher.PluginBinary):
    def __init__(self, data, item):
        self.data = data
        self.item = item
        self.log = logging.getLogger("EsouiBinary")
    
    def install(self, directory):
        dest = os.path.realpath(directory)
        self.log.info("installing %s to %s" % (self.item.title, dest))
        zip = zipfile.ZipFile(self.data, "r")
        toplevel = {}
        for entry in zip.namelist():
            parts = entry.split("/")
            if ".." in parts or parts[0] == "":
                raise Exception("zip is breaking out its directory")
            toplevel[parts[0]] = parts[0]
            base = parts[0]

        pluginPath = os.path.join(dest, base)
        if len(toplevel) > 1:
            # raise Exception("looks like the archive has multiple directories")
            self.log.warning("looks like the archive has multplie directories. relocate to %s" % (dest))
            dest = os.path.join(dest, self.item.title.title().replace(" ", ""))
            pluginPath = dest
            try:
                os.makedirs(pluginPath)
            except:
                pass

        if self.item.path and os.path.exists(self.item.path):
            self.log.info("cleanup %s" % (self.item.path))
            shutil.rmtree(self.item.path)

        if os.path.exists(pluginPath):
            self.log.info("cleanup %s" % (pluginPath))
            shutil.rmtree(pluginPath)
        
        self.log.info("unzipping to %s" % (pluginPath))
        self.item.path = pluginPath

        zip.extractall(dest)
        return pluginPath
    