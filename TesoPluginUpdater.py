#!/usr/bin/env python

import os
import sys

from fetcher import PluginRegistry
import logging

#logging.basicConfig(level=logging.DEBUG)

plugindir = os.path.realpath("../AddOns")
pluginconf = os.path.join(plugindir, "plugins.json")
registry = PluginRegistry()

def do_help(name):
    print "Usage: %s --update" % name
    print "       %s --add <source> <id>" % name
    print "       %s --remove <source> <id>" % name
    print "       %s --list" % name
    print "       %s --help" % name
    print ""
    print "Actions:"
    print "       --update: updates all plugins"
    print "       --remove: removes a plugin"
    print "       --add:    adds the given plugin"
    print "       --list:   lists all plugins"
    print "       --help:   shows this help"
    print ""
    print "AddOns: %s" % (plugindir)

def do_list(args):
    print "Plugins:"
    for plugin in registry.values():
        print "  %-15s %s (%s)" % ("%s:%s" % (plugin.source, plugin.id), plugin.title, plugin.version)
    print ""

def do_update(args):
    sources = registry.sources
    count = 0
    print "Check for updates on %d plugins." % (len(registry))
    for plugin in registry.values():
        sys.stdout.write("  %-50s [CHECK]" % (plugin.title))
        sys.stdout.flush()
        source = sources[plugin.source]
        metaItem = source.fetchMetaData(plugin)
        updated = plugin.wasUpdated(metaItem)
        if updated:
            sys.stdout.write(" [FETCH]")
            sys.stdout.flush()
            data = source.fetchPlugin(plugin)
            sys.stdout.write(" [INSTALL]")
            sys.stdout.flush()
            data.install(plugindir)
            plugin.updateInfo(metaItem)
            count += 1
        print " [DONE]"
    print "Checking for updates done. %d updates installed." % (count)

def do_remove(args):
    id = "%s:%s" % (args[0], args[1])
    if not id in registry:
        raise Exception("plugin %s not found" % (id))
    print "Remove %s" % (registry[id].title)
    registry[id].uninstall()
    del registry[id]

def do_add(args):
    source = args[0]
    id = args[1]
    print "Adding plugin %s from source %s" % (id, source)
    plugin = registry.addNew(source, id)
    print "Installing %s (%s)" % (plugin.title, plugin.version)
    data = registry.sources[source].fetchPlugin(plugin)
    data.install(plugindir)
    
def main(name, args):
    saveOnExit = False
    if len(args) == 0:
        do_help(name)
        return
    elif args[0] == "--help":
        do_help(name)
        return
    
    registry.load(open(pluginconf, "rb"))
    if args[0] == "--list":
        do_list(args)
    elif args[0] == "--remove":
        do_remove(args[1:])
        saveOnExit = True
    elif args[0] == "--add":
        do_add(args[1:])
        saveOnExit = True
    elif args[0] == "--update":
        do_update(args[1:])
        saveOnExit = True
    else:
        print "Unknown action: %s" % (args[0])
        do_help(name)

    if saveOnExit:
        registry.save(open(pluginconf, "wb"))

main(sys.argv[0], sys.argv[1:])

