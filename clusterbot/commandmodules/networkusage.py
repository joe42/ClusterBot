from clusterbot.ssh import *
from clusterbot.events.CachedEvent import CachedEvent
from string import Template
from clusterbot.util.timer import Timer

class networkusage():
    def __init__(self, name, tty, description='Displays an overview of the network usage.' ):
        self.description = description;
        self.__tty = tty;
        self.name = name;
        self.lastResult = None;
        self.timer = Timer(60);
    def getDescription(self):
        return self.description
    def getName(self):
        return self.name
    def executeCommand(self, mess, args):
        """ Displays an overview of the network usage. """
        ret  = ''
        if not self.lastResult is None and not self.timer.rings():
            ret = self.lastResult;
        else:
            self.lastResult = None;
            self.result = ranycmd(self.__tty, 'pdsh -a "ifstat -z 1/1 1 "|dshbak -c;');
            self.result = '\n'.join(self.result)
            self.result = Template('$result').safe_substitute(self.__dict__, result=self.result)
            self.lastResult = self.result;
            ret = self.result
        return ret

def returnInstance(tty, args):
    return networkusage('networkusage', tty);