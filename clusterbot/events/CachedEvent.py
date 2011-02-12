import time
from Event import Event

class CachedEvent(Event):
    def __init__(self, name, cache_duration=60, description="", defaultMessage=""):
        super(CachedEvent, self).__init__(name, description, defaultMessage);
        self.cache_duration = cache_duration;
        self.timeStamp = time.time() + cache_duration; #cache has expired
    def cacheExpired(self):
        return self.timeStamp + self.cache_duration < time.time();
    def setEventMessage(self):
        """does nothing if cache is not expired and resets the timeStamp otherwise
            Should be overridden in subclass, where the first call should be super(CachedEvent,self).seteventMessage().
        """
        if not self.cacheExpired():
            return False;
        self.timeStamp = time.time();
        return True;
        
