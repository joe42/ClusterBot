import unittest
import XMLParserTest
import EventDrivenShellClusterBotTest 
import MyXMLReaderTest 
import stringtest

if __name__ == "__main__":     
    suite1 = XMLParserTest.suite()
    suite2 = EventDrivenShellClusterBotTest.suite()
    suite3 = MyXMLReaderTest.suite()
    suite4 = stringtest.suite()
    alltests = unittest.TestSuite((suite1, suite2, suite3, suite4))
    runner = unittest.TextTestRunner()
    runner.run(alltests)
