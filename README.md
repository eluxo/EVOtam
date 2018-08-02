= Eluxos Very Own TESO Addon Manager

This needs python2 with pycurl and lxml installed on windows. I actually use 
it from cygwin which works quite nice. I have build pycurl via pip, which needs
openssl-dev and gcc packages installed in cygwin.

It is currently not meant to be just used by everyone as it needs some serious
knowlage about the tools mentioned above. I just wanted to build something on
my own as I do not want to trust minion. If this is some use for anyone else,
please feel free to fork or just use it right away.

== Usage

It basically needs a plugin.json that contains just an empty object to work.
To create it, you can use
```bash
echo '{}' >plugin.json
```

== Commandline Interface

```
Usage: TesoPluginUpdater.py --update
       TesoPluginUpdater.py --add <source> <id>
       TesoPluginUpdater.py --remove <source> <id>
       TesoPluginUpdater.py --list
       TesoPluginUpdater.py --help

Actions:
       --update: updates all plugins
       --remove: removes a plugin
       --add:    adds the given plugin
       --list:   lists all plugins
       --help:   shows this help

AddOns: /cygdrive/c/Users/nexus/Documents/Elder Scrolls Online/live/AddOns
```

