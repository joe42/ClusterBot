from clusterbot.events.XMLEventParser import *
import unittest
#import xmpp
import sys, inspect

class XMLParserTest(unittest.TestCase):
	inputFile = os.path.dirname(__file__)+ "/ExceedingCPUTempEvent2.xml"
	#print inputFile
	result = u"from clusterbot.ssh import *\n\
from clusterbot.events.CachedEvent import CachedEvent\n\
from clusterbot.util.string import *\n\
from string import Template\n\
\n\
class ExceedingCPUTempEvent2(CachedEvent):\n\
    def __init__(self, name, tty, x, description='An exceedingly obvious testing stub.' ):\n\
        super(ExceedingCPUTempEvent2, self).__init__(name, 60, description, defaultMessage='The event ExceedingCPUTempEvent2 did not yet occure.');\n\
        self.tty = tty;\n\
        self.x = x;\n\
    def seteventMessage(self):\n\
        #call to super.seteventmessage(); for caching:\n\
        super(ExceedingCPUTempEvent2,self).seteventMessage();\n\
        self.result = ranycmd(self.tty, 'sensors');\n\
        newmessage = '';\n\
        self.setTriggered(False)\n\
        for line in self.result:\n\
            cputemp = regSearchInt('(\d+).?.?.?.?C', line, 1);\n\
            if not None in [ cputemp ] and cputemp > 90:\n\
                newmessage += Template('CPU temperature hit critical limit: $cputemp\\n').safe_substitute(self.__dict__, result=self.result, cputemp=cputemp)\n\
                self.setTriggered()\n\
        if self._getMessage() != newmessage:\n\
            self._setmessage(newmessage)\n\
            self.updated();\n\
\n\
def returnInstance(tty, args):\n\
    if 'x' in args:\n\
        x = args['x'];\n\
    else:\n\
        x = 0\n\
    return ExceedingCPUTempEvent2('ExceedingCPUTempEvent2', tty, x=x);";
		

	def test_parseEvent(self): 
		ret = parseEvent(self.inputFile)
		#print ret 
		#print self.result
		self.assertEquals(ret, self.result) 
	

def suite():
	suite = unittest.TestSuite()
	module = sys.modules[__name__]
	for name in dir(module):
		obj = getattr(module, name)
		if inspect.isclass(obj) and obj.__module__ == __name__:
			suite.addTest(unittest.TestLoader().loadTestsFromTestCase(obj))
	return suite



