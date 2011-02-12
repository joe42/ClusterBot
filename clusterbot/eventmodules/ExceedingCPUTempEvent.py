from clusterbot.ssh import *
from clusterbot.util.string import *
from clusterbot.events.CachedEvent import CachedEvent
"""
Event modules need to define a function returnInstance(__tty) which returns the instance with an Event subclass. 
"""
class ExceedingCPUTempEvent(CachedEvent):
    def __init__(self, name, tty, tempMax=90 ):
        super(ExceedingCPUTempEvent, self).__init__(name, 60, "Triggered if any CPU enters a critical range.", defaultMessage="Temperature could not yet be measured.");
        self.tempMax = tempMax
    def seteventMessage(self):
        #call to super.seteventmessage(); for caching:
        super(ExceedingCPUTempEvent,self).seteventMessage(); 
        newmessage = "";
        for line in rsensors(self.__tty):
            cluster = regSearchString("([^:]*)", line);
            cpu = regSearchString("(Core\d*)", line);
            temp = regSearchInt('(\d+).?.?.?.?C', line);
            self.setTriggered(False)
            if not None in [cluster, cpu, temp] and temp > self.tempMax:
                newmessage += "%s on %s has a critical temperature of %i C \n" % (cpu, cluster, temp)
                self.setTriggered()
        if super(ExceedingCPUTempEvent,self)._getMessage() != newmessage:
            self.updated();
            
def returnInstance(tty, args):
    return ExceedingCPUTempEvent("ExceedingCPUTempEvent", tty);