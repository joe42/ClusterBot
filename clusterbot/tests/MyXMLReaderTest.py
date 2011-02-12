from clusterbot.util.MyXMLReader import MyXMLReader
import unittest
import os
#import xmpp

class MyXMLReaderTest(unittest.TestCase):
    testobj = MyXMLReader( os.path.dirname(__file__)+"/testconfig.xml")
    def test_hasAttribute(self): 
        self.assertTrue(self.testobj.hasAttribute("headnode","user"))
        self.assertTrue(self.testobj.hasAttribute("headnode","ip"))
        self.assertTrue(self.testobj.hasAttribute("jabber","jid"))
        self.assertTrue(self.testobj.hasAttribute("jabber","password"))
        self.assertTrue(self.testobj.hasAttribute("whitelist","jid"))
        self.assertFalse(self.testobj.hasAttribute("whitelist","jiddddd"))
        self.assertFalse(self.testobj.hasAttribute("whitelistt","jid"))
        
    def test_getAttribute(self): 
        self.assertEquals(self.testobj.getAttribute("headnode","user"), "jmueller")
        self.assertEquals(self.testobj.getAttribute("headnode","ip"), "141.76.90.33")
        self.assertEquals(self.testobj.getAttribute("jabber","jid"), "clusterbot@jabber.org")
        self.assertEquals(self.testobj.getAttribute("jabber","password"), "123456")
        self.assertTrue("clusterbot@jabber.org" in self.testobj.getAttribute("whitelist","jid"))
        self.assertTrue("gilgamesh@jabber.ccc.de" in self.testobj.getAttribute("whitelist","jid"))
        self.assertRaises(ValueError, self.testobj.getAttribute,"whitelist","jiddddd")
        self.assertRaises(ValueError, self.testobj.getAttribute,"whitelistt","jid")
        
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(MyXMLReaderTest)
    return suite

