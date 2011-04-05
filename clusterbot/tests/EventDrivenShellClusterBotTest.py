import unittest 
from xmpp.protocol import Message
from clusterbot.EventDrivenShellClusterBot import EventDrivenShellClusterBot
import sys, inspect

class EventDrivenShellClusterBotTest(unittest.TestCase):
	def setUp(self): 
		self.testobj = EventDrivenShellClusterBot("testuser","testpwd",[], None, None, None, debug=True)	
		self.subscriber="testsubscriber"
		self.nonexistentEvent="NoneExistantEvent"
		self.existentEvent="ExceedingCPUTempEvent"

	def tearDown(self): 
		self.testobj.quit();
		self.testobj = None;

	def test_subscribe_eventdoesnotexist(self): 
		ret = self.testobj.subscribe(Message(frm=self.subscriber), self.nonexistentEvent)
		self.assertEquals(ret, "The event %s is not available for subscription." % self.nonexistentEvent, "the event should not exist and hence not be available for subscription") 
		ret = self.testobj.unsubscribe(Message(frm=self.subscriber), self.nonexistentEvent)
		self.assertEquals(ret, "The event %s is not available for subscription." % self.nonexistentEvent, "the event should not exist and hence noone should have been able to subscribe to it") 
	
	def test_subscribe_eventdoesexist(self): 
		self.testobj.importnewevents(None,[]);
		
		ret = self.testobj.unsubscribe(Message(frm=self.subscriber), self.existentEvent)
		self.assertEquals(ret, 'You are not subscribed to the event '+self.existentEvent, "this user has not yet subscribed to the event") 
		
		ret = self.testobj.subscribe(Message(frm=self.subscriber), self.existentEvent)
		self.assertEquals(ret, 'You are now subscribed to the event: '+ self.existentEvent, "the event should exist and be available for subscription") 

		ret = self.testobj.subscribe(Message(frm=self.subscriber), self.existentEvent)
		self.assertEquals(ret, 'You are already subscribed to the event: '+ self.existentEvent, "the user should already be subscribed to the event") 
	
		ret = self.testobj.unsubscribe(Message(frm=self.subscriber), self.existentEvent)
		self.assertEquals(ret, 'You are now unsubscribed from the event '+ self.existentEvent, "the user should be unsubscribed to the event") 
		
		ret = self.testobj.unsubscribe(Message(frm=self.subscriber), self.existentEvent)
		self.assertEquals(ret, 'You are not subscribed to the event '+self.existentEvent, "this user should have been unsubscribed from the event")



def suite():
	suite = unittest.TestSuite()
	module = sys.modules[__name__]
	for name in dir(module):
		obj = getattr(module, name)
		if inspect.isclass(obj) and obj.__module__ == __name__:
			suite.addTest(unittest.TestLoader().loadTestsFromTestCase(obj))
	return suite