from jabberbot import botcmd 
from clusterbot.ShellClusterBot import ShellClusterBot
from clusterbot.events.XMLEventParser import * 
import sys 
import time
import clusterbot.eventmodules;
import os, pkgutil
import threading;
import thread
"""
Todo: manual import function X
import function for xml modules X
implement listevents X
implement anycommand in ssh X
load credentials and allowedJIDs from xml File X
"""

""""""
class EventDrivenShellClusterBot(ShellClusterBot):
    def __init__(self, jabberID, jabberPW, allowedJIDs, headnodeIP, headnodeUser, headnodePW, debug=False): 
        super( EventDrivenShellClusterBot, self ).__init__(jabberID, jabberPW, allowedJIDs, headnodeIP, headnodeUser, headnodePW, debug);
        self.events = {};  
        self.eventsLock = thread.allocate_lock();
        self.thread_killed = False;
    
    def connect_callback(self):
        """Overwrites :meth:`clusterbot.ShellClusterBot.ShellClusterBot.connect_callback` to start event polling at connection time."""
        super( EventDrivenShellClusterBot, self ).connect_callback();
        self.debug("Registering handler for event polling.")
        self.__startEventPollingThread()
    
    def __killEventPollingThread(self):
        self.thread_killed = True;
        
    def __startEventPollingThread(self):
        self.thread_killed = False;
        th = threading.Thread( target = self.__pollEvents);
        th.start(); 
    
    def quit(self):
        """Overwrites :meth:`clusterbot.ShellClusterBot.ShellClusterBot.quit`."""
        super( EventDrivenShellClusterBot, self ).quit(); 
        self.__killEventPollingThread();
    
    @botcmd
    def subscribe( self, mess, args):
        """Subscribe to an event."""
        user = mess.getFrom()
        ret = "";
        self.eventsLock.acquire();
        if not args in self.events:
            ret = "The event %s is not available for subscription." % args;
        else:
            if self.events[args].isSubscribed(user):
                ret = 'You are already subscribed to the event: '+args;
            else:
                self.events[args].subscribe(user);
                self.log( '%s subscribed to the event: %s' % (user, args));
                ret = 'You are now subscribed to the event: '+args;
        self.eventsLock.release();
        return ret;
        
    @botcmd
    def unsubscribe( self, mess, args):
        """Unsubscribe from an event."""
        user = mess.getFrom()
        ret = "";
        self.eventsLock.acquire();
        if not args in self.events:
            ret = "The event %s is not available for subscription." % args;
        else:
            if self.events[args].unsubscribe(user):
                self.log( '%s unsubscribed from the event %s.' % (user, args))
                ret = 'You are now unsubscribed from the event '+args
            else:
                ret = 'You are not subscribed to the event '+args
        self.eventsLock.release();
        return ret;
    
    def broadcast( self, message, users=None):
        """Broadcasts the message to a list of users given as jabber ids."""
        if users == None:
            users = self.users;
        for user in users:
            self.send( user, message)
        
    @botcmd
    def createevent(self, mess, args):
        """Creates a new event module from an XML string."""
        return createEventFromString(args);
       
    @botcmd
    def importnewevents(self, mess, args):
        """Loads new event modules from the package clusterbot.eventmodules"""
        pkgpath = os.path.dirname(clusterbot.eventmodules.__file__);
        for newmodulename in [name for _, name, _ in pkgutil.iter_modules([pkgpath])]:
            __import__("clusterbot.eventmodules."+newmodulename);
            newmodule = sys.modules["clusterbot.eventmodules."+newmodulename];
            newevent = newmodule.returnInstance(self.__tty,args);
            try:
                getattr(newevent, 'getName');
            except AttributeError:
                self.log("The extension %s does not provide the Event interface!" % newmodulename);
                continue;
            try:
                getattr(newmodule, 'returnInstance');
            except AttributeError,TypeError:
                self.log("The event %s does not provide the returnInstance(__tty, args) function!" % newevent.getName());
                continue;
            self.eventsLock.acquire();
            if newevent.getName() in self.events:
                self.eventsLock.release();
                self.log("The event %s already exists, please rename your extension!" % newevent.getName());
                continue;
            self.events[newevent.getName()] = newevent;
            self.eventsLock.release();
        return "Alright, use the listevents command to get an overview on the imported modules.";

    @botcmd
    def listevents( self, mess, args):
        """Lists events to subscribe to."""
        ret = "";
        self.eventsLock.acquire();
        for names in self.events:
            ret += "Name: "+names+"\n";
            ret += "Desc: "+self.events[names].getDescription()+"\n";
        self.eventsLock.release();
            
        return ret;


    def __pollEvents(self):
        """Polls for new events. 
        Must be called in another thread. Otherwise it blocks.
        """
        while not self.thread_killed:
            for i in range(10):
                time.sleep(1)
            if self.thread_killed:
                return
            self.eventsLock.acquire();
            for name in self.events:
                event = self.events[name];
                observers = event.getObservers()
                self.debug("Checking event %s if it has observers and if it has triggered." % event.getName())
                if len(observers) > 0 and event.isTriggered():
                    self.debug("Broadcasting event %s, with message: %s to %s" % (event.getName(),event.getEventMessage(),str(observers)))
                    self.broadcast(event.getEventMessage(), observers)
            self.eventsLock.release();



