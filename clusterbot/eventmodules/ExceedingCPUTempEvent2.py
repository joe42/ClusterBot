from clusterbot.ssh import *
from clusterbot.events.CachedEvent import CachedEvent
from clusterbot.util.string import *
from clusterbot.ssh import *
from string import Template

class ExceedingCPUTempEvent2(CachedEvent):
    def __init__(self, name, tty, x, description='An exceedingly obvious testing stub.' ):
        super(ExceedingCPUTempEvent2, self).__init__(name, 60, description, defaultMessage='The event ExceedingCPUTempEvent2 did not yet occure.');
        self.x = x;
        self.__tty = tty;
    def setEventMessage(self):
        #call to super.seteventmessage(); for caching:
        print "eventmsg1"
        if not super(ExceedingCPUTempEvent2,self).setEventMessage():
            return;
        print "eventmsg2"
        self.result = ranycmd(self.__tty, 'sensors');
        print self.result
        newmessage = '';
        self.setTriggered(False)
        for line in self.result:
            cputemp = regSearchInt('(\d+).?.?.?.?C', line, 1);
            if not None in [ cputemp ]: 
                print "tmp = %i" % cputemp
            if not None in [ cputemp ] and cputemp > 10:
                print "triggered"
                newmessage += Template('CPU temperature hit critical limit: $cputemp\n').safe_substitute(self.__dict__, result=self.result, cputemp=cputemp)
                self.setTriggered()
        if super(ExceedingCPUTempEvent2,self)._getMessage() != newmessage:
            self._setmessage(newmessage)
            self.updated();

def returnInstance(tty, args):
    if "x" in args:
        x = args["x"];
    else:
        x = 0
    return ExceedingCPUTempEvent2('ExceedingCPUTempEvent2', tty, x=x);