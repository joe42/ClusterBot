"""
Baseclass of events for ClusterBot: L{ClusterBot<ClusterBot>}

Subclasses need to be implemented in the events package.
They need to override seteventMessage().
"""
class Event(object):
    def __init__(self, name, description="", defaultMessage=""):
        self.name = name;
        self.description = description;
        self.defaultMessage = defaultMessage;
        self.message = None;
        self.updatedFlag = False;
        self.triggered = False;
        self.observers = []
    def getName(self):
        return self.name;
    def getDescription(self):
        return self.description;
    def setDescription(self,value):
        self.description = value;
    def getObservers(self):
        return self.observers;
    def subscribe(self, observer):
        self.observers.append(observer);
    def unsubscribe(self, observer):
        try:
            self.observers.remove(observer);
        except:
            return False;
        return True;
    def isSubscribed(self, observer):
        """:returns: true iff listener is subscribed to this event"""
        return observer in self.observers;
    def setDefaultMessage(self, val):
        """sets the default Message which is returned by getEventMessage if the event message is None"""
        self.defaultMessage = val;
    def _getMessage(self):
        return self.message;
    def getEventMessage(self):
        """Gets the event message.
        This is no simple getter method. It also sets the updated status to False.
        :returns: the current message of this event or defaultMessage iff the current message is None
        """
        self.updated(False);
        if self.message == None:
            self.message = self.defaultMessage;
        return self.message;
    def _setmessage(self, message):
        self.message = message; 
    def setEventMessage(self):
        """Stub to set the event message. It should be overridden in subclass. 
        Subclasses have to set the event message, call updated() when the message changed as well as setTriggered() with the appropriate parameter
        """
        pass;
    
    def updated(self, bool=True):
        self.updatedFlag = bool;
    def isUpdated(self, bool=True):
        """:returns: True iff the event message changed after the last call to getEventMessage"""
        self.updatedFlag = bool;
    def setTriggered(self, bool=True):
        """Sets the status of the event. 
        States if it is triggered or not.
        """
        self.triggered = bool;
    def isTriggered(self):
        """Gets the status of the event. 
        States if it is triggered or not. This is no simple getter method. It updates the event by executing setEventMessage.
        """
        self.setEventMessage();
        return self.triggered;

    
