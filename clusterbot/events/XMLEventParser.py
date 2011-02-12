from clusterbot.util.string import *
import xml.sax 
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os.path
from clusterbot.util.ClassBuilder import ClassBuilder
#TODO: support other numbers than int
#TODO: overwrite event name, introduce description (also to test)
#TODO: Use a pattern like a Builder to improve readabilityand extensibility 

"""
Modlue for creating Events from XML files.

"""
class EventBuilder(ClassBuilder):
    def __init__(self):
        super(EventBuilder, self).__init__();
        self.superClass = None;
        self.command = None;
        self.message = None;
        self.description = None;
        self.regex = {}
        self.tests = []
        
    def getDescription(self):
        ret=""
        if not self.description == None:
            ret = self.description
        return ret

    def __getRegexStringSearches(self):
        ret = ""
        for name in self.regex:
            if self.regex[name].type == 'str':
                ret += "%s = regSearchString('%s', line, %i);\n" % (name, self.regex[name].regex, self.regex[name].matchnr)
        return ret
    
    def __getRegexIntSearches(self):
        ret = ""
        for name in self.regex:
            if self.regex[name].type == 'int':
                ret += "%s = regSearchInt('%s', line, %i);\n" % (name, self.regex[name].regex, self.regex[name].matchnr)
        return ret

    def getRegexSearches(self, type="all"):
        ret = ""
        if type is "str":
            ret = self.__getRegexStringSearches();  
        elif type is "int":
            ret = self.__getRegexIntSearches(); 
        elif type is "all":
            ret += self.__getRegexStringSearches();
            ret += self.__getRegexIntSearches(); 
        else:
            raise ValueError,"getRegexSearches does not accept the type \""+type+"\"";
        return ret;

    def getRegexNamesAsParameters(self,startWithComma=False,withDefaultValues=False):
        ret = self._getParametersFromDict(self.regex, startWithComma, withDefaultValues);
        return ret
    
    
    def getTestsAsBooleanExpression(self):
        ret = "";
        if len(self.tests) > 0:
            ret = " and " + " and ".join(self.tests)
        return ret
    
class XMLEventHandler(ContentHandler):  
    """Assembles information for finally creating the  string representing a Python module"""  
    def __init__(self):
        self.eventBuilder = EventBuilder();
    def startElement(self, tagname, attrs):
        if tagname == 'event': 
            self.eventBuilder.className = attrs.get('name', None)
            self.eventBuilder.superClass = attrs.get('is', None)
        if tagname == 'description': 
            self.eventBuilder.description = attrs.get('desc', None)
        if tagname == 'param': 
            name = attrs.get('name', None)
            defaultvalue = eval(attrs.get('default', None))
            self.eventBuilder.parameters[name] = defaultvalue
        if tagname == 'command': 
            self.eventBuilder.command = attrs.get('cmd', None)
        if tagname == 'regex': 
            name = attrs.get('name', None)
            regex = attrs.get('regex', None)
            matchnr = attrs.get('matchnr', 1)               
            type = attrs.get('type', 'int')               
            self.eventBuilder.regex[name] = RegExData(regex,matchnr,type)
        if tagname == 'test': 
            self.eventBuilder.tests.append(attrs.get('test', None))
        if tagname == 'message': 
            self.eventBuilder.message = attrs.get('text', None)
            
    def getpythonfile(self):
        # if None in self.options.keys() or None in self.options.values():
        #    print "Warning, unspecified attribute"
        if self.eventBuilder.superClass == "CachedEvent":
            return self.constructCachedEvent();
        

    def constructCachedEvent(self):    
        cache_duration = 60;
        if 'cache_duration' in self.eventBuilder.parameters:
            cache_duration = self.eventBuilder.parameters['cache_duration'];
            
        """initialize constructor event parameters"""
        description = self.eventBuilder.getDescription()
        constructorParametersC = self.eventBuilder.getConstructorParameters(startWithComma=True)
        instanceVariables = self.eventBuilder.getInstanceVariableAssignments()
        constructorParametersCV = self.eventBuilder.getConstructorParameters(startWithComma=True, withDefaultValues=True)
        parameters = self.eventBuilder.getConstructorParameterAssignments()
        searches = self.eventBuilder.getRegexSearches()
        regexVarList = self.eventBuilder.getRegexNamesAsParameters()
        regexVarListCV = self.eventBuilder.getRegexNamesAsParameters(startWithComma=True,withDefaultValues=True)
        tests = self.eventBuilder.getTestsAsBooleanExpression()
    
        #if len(self.eventBuilder.parameters) > 0:
        #    constructorParametersCV = ''.join([", %s='%s'" % (name,value) for (name,value) in self.eventBuilder.parameters.items() if type(value) is str]);
        #    constructorParametersCV += ''.join([", %s=%i" % (name,value) for (name,value) in self.eventBuilder.parameters.items() if not type(value) is str]);
    

        self.pythonfile = "\
from clusterbot.ssh import *\n\
from clusterbot.events.CachedEvent import CachedEvent\n\
from clusterbot.util.string import *\n\
from string import Template\n\
\n\
class "+self.eventBuilder.className+"(CachedEvent):\n\
    def __init__(self, name, tty"+constructorParametersC+", description='"+description+"' ):\n\
        super("+self.eventBuilder.className+", self).__init__(name, "+str(cache_duration)+", description, defaultMessage='The event "+self.eventBuilder.className+" did not yet occure.');\n\
        self.tty = tty;\n"\
+indentLines(instanceVariables,8)+"\
    def seteventMessage(self):\n\
        #call to super.seteventmessage(); for caching:\n\
        super("+self.eventBuilder.className+",self).seteventMessage();\n\
        self.result = ranycmd(self.tty, '"+self.eventBuilder.command+"');\n\
        newmessage = '';\n\
        self.setTriggered(False)\n\
        for line in self.result:\n"\
+indentLines(searches,12)+"\
            if not None in [ "+regexVarList+" ]"+tests+":\n\
                newmessage += Template('"+self.eventBuilder.message+"').safe_substitute(self.__dict__, result=self.result"+regexVarListCV+")\n\
                self.setTriggered()\n\
        if self._getMessage() != newmessage:\n\
            self._setmessage(newmessage)\n\
            self.updated();\n\
\n\
def returnInstance(tty, args):\n"\
+indentLines(parameters,4)+"\
    return "+self.eventBuilder.className+"('"+self.eventBuilder.className+"', tty"+constructorParametersCV+");";
        return self.pythonfile;

        
def parseEvent(xmlfile): 
    """Parse the file xmlfile and return a Python module as a string."""
    parser = make_parser()
    # Tell the parser we are not interested in XML namespaces
    #parser.setFeature(feature_namespaces, 0)
    xmleventhandler = XMLEventHandler()
    # Tell the parser to use our handler
    parser.setContentHandler(xmleventhandler)
    # Parse the input
    parser.parse(open(xmlfile))
    #[os.path.join(directory, f) 
#               for f in fileList
#                if os.path.splitext(f)[1] in fileExtList]
    #os.path.dirname(eventmodules.__file__)+"\\ExceedingCPUTempEvent2.xml"
    return xmleventhandler.getpythonfile();

def createEventFromString(xmlstring): 
    """Parse the string xmlstring and create a Python module with the name of the event."""
    parser = make_parser()
    xmleventhandler = XMLEventHandler()
    #parser.setContentHandler(xmleventhandler)
    xml.sax.parseString(xmlstring,xmleventhandler)
    f = open('clusterbot/eventmodules/'+os.path.basename(xmleventhandler.eventBuilder.className)+".py", 'w');
    f.write(xmleventhandler.getpythonfile());
    return xmleventhandler.getpythonfile()
