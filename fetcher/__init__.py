import json
import logging
import shutil
import os

class PluginSource(object):
    def newItem(self):
        raise Exception("not implemented: newItem(self) missing on child")
    
    def fetchMetaData(self, item):
        raise Exception("not implemented: fetchMetaData(self, item) missing on child")
    
    def fetchPlugin(self, item):
        raise Exception("not implemented: fetchPlugin(self, item) missing on child")
    
class PluginItem(object):
    def load(self, item):
        for key, value in item.iteritems():
            setattr(self, key, value)
    
    def wasUpdated(self, metaItem):
        if metaItem.version != self.version:
            return True
        if metaItem.updated != self.updated:
            return True
        return False
    
    def updateInfo(self, metaItem):
        metaData = metaItem.toDict()
        del metaData["path"]
        self.load(metaData)
    
    def uninstall(self):
        if os.path.exists(self.path):
            shutil.rmtree(self.path)
    
    def toDict(self, additional = []):
        rc = {}
        fields = ["title", "version", "updated", "id", "source", "path"]
        fields += additional
        for field in fields:
            rc[field] = getattr(self, field)
        return rc

class PluginBinary(object):
    def install(self, directory):
        raise Exception("not implemented: install(self, directory) missing on child")
        
import esoui

class PluginSourceMap(dict):
    def __init__(self):
        self[esoui.EsouiPluginSource.name] = esoui.EsouiPluginSource()

class PluginRegistry(dict):
    def __init__(self):
        self.sources = PluginSourceMap()
        self.log = logging.getLogger("PluginRegistry")

    def load(self, fp):
        data = json.load(fp)
        for item in data.values():
            self.log.debug("loading %s:%s" % (item["source"], item["id"]))
            source = item["source"]
            entry = self.sources[source].newItem()
            entry.load(item)
            self["%s:%s" % (entry.source, entry.id)] = entry

    def addNew(self, source, id):
        pluginSource = self.sources[source]
        plugin = pluginSource.newItem()
        plugin.source = source
        plugin.id = id
        entry = pluginSource.fetchMetaData(plugin)
        self["%s:%s" % (entry.source, entry.id)] = entry
        return entry
    
    def save(self, fp):
        self.log.info("writing to file")
        items = {}
        for key, item in self.iteritems():
            self.log.info("saving %s for version %s (%s)" % (item.title, item.version, item.updated))
            items[key] = item.toDict()
        json.dump(items, fp, indent = 2, sort_keys = True)


