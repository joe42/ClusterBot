from Event import Event
from xml.sax import saxutils

class EventFactory(Event):
    def __init__(self, name, cache_duration=60, description="", defaultMessage=""):
        super(EventFactory, self).__init__(name, description, defaultMessage);
        self.cache_duration = cache_duration;
        self.timeStamp = time.time() + cache_duration; #cache has expired
    def generateEvent(self):
        ;
    def seteventMessage(self):
        """does nothing if cache is not expired and resets the timeStamp otherwise
            Should be overridden in subclass, where the first call should be super(CachedEvent,self).seteventMessage().
        """
        if not self.cacheExpired():
            return;
        self.timeStamp = time.time();
        
 