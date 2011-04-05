import unittest
import sys, inspect
import clusterbot.tests
import pkgutil
from unittest import TestCase

def getTestSuitesOfPackage(package):
    ret = [] 
    for importer, modname, ispkg in pkgutil.walk_packages(path=package.__path__,
                                                      prefix=package.__name__+'.',
                                                      onerror=lambda x: None):
        ret.extend(getTestSuiteOfModule(modname))
    return ret;

def getTestSuiteOfModule(moduleName):
    ret = []
    __import__(moduleName)
    module = sys.modules[moduleName]
    for name in dir(module):
        obj = getattr(module, name)
        if inspect.isclass(obj) and obj.__module__ == moduleName and issubclass(obj, unittest.TestCase):
            ret.append(unittest.TestLoader().loadTestsFromTestCase(obj))
    return ret;

if __name__ == "__main__":    
    testSuites = getTestSuitesOfPackage(clusterbot.tests)
    alltests = unittest.TestSuite(tuple(testSuites))
    runner = unittest.TextTestRunner()
    runner.run(alltests)
