from clusterbot.util.string import *
import unittest

class StringTest(unittest.TestCase):
    def setUp(self): 
        self.testString = "The Answer to the Ultimate Question of Life, the Universe, and Everything is 42."
        self.matchingRegex = "([0-9]+)"
        self.matchingRegexSecondGroup = "(.*)([0-9]{2})"
        self.notMatchingRegex = "(23)"
        self.notMatchingRegexSecondGroup = "(.*)(23)"
        self.indentedLine = ""
        self.lineToIndent = ""
        
    def tearDown(self): 
        pass;
        
    def test_regSearchInt(self): 
        self.assertEquals(regSearchInt(self.notMatchingRegex, self.testString), None)
        self.assertEquals(regSearchInt(self.notMatchingRegex, self.testString, 1), None) 
        self.assertEquals(regSearchInt(self.matchingRegex, self.testString), 42)
        self.assertEquals(regSearchInt(self.matchingRegex, self.testString, 1), 42) 
        self.assertEquals(regSearchInt(self.matchingRegexSecondGroup, self.testString, 2), 42) 
        
    def test_regSearchString(self): 
        self.assertEquals(regSearchString(self.notMatchingRegex, self.testString), None)
        self.assertEquals(regSearchString(self.notMatchingRegex, self.testString, 1), None) 
        self.assertEquals(regSearchString(self.matchingRegex, self.testString), "42")
        self.assertEquals(regSearchString(self.matchingRegex, self.testString, 1), "42")  
        
    def test_indentLines(self): 
        self.assertEquals(indentLines("", 1), "")
        self.assertEquals(indentLines("one line \n", 1), " one line \n")
        self.assertEquals(indentLines("zero indent one line \n", 0), "zero indent one line \n")
        self.assertEquals(indentLines("two lines \ntwo lines \n", 1), " two lines \n two lines \n")
        self.assertEquals(indentLines("two lines \ntwo lines \n", 0), "two lines \ntwo lines \n") 
        
def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase(StringTest)
    return suite

