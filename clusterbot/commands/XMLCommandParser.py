from clusterbot.util.string import *
import xml.sax 
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import os.path
from clusterbot.util.ClassBuilder import ClassBuilder
#ToDo: support other numbers than int
        
class CommandBuilder(ClassBuilder):
    def __init__(self):
        super(CommandBuilder, self).__init__();
        self.command = None;
        self.message = None;
        self.description = None;
        self.regex = {}
        
    def getDescription(self):
        ret=""
        if not self.description == None:
            ret = self.description;
        return ret

    def __getRegexStringSearches(self):
        ret = ""
        for name in self.regex:
            if self.regex[name].type == 'str':
                ret += "%s = regSearchString('%s', self.result, %i);\n" % (name, self.regex[name].regex, self.regex[name].matchnr)
        return ret
    
    def __getRegexIntSearches(self):
        ret = ""
        for name in self.regex:
            if self.regex[name].type == 'int':
                ret += "%s = regSearchInt('%s', self.result, %i);\n" % (name, self.regex[name].regex, self.regex[name].matchnr)
        return ret

    def getRegexSearches(self, type="all"):
        ret = ""
        if type == "str":
            ret = self.__getRegexStringSearches();  
        elif type == "int":
            ret = self.__getRegexIntSearches(); 
        elif type == "all":
            ret += self.__getRegexStringSearches();
            ret += self.__getRegexIntSearches(); 
        else:
            raise ValueError,"getRegexSearches does not accept the type \""+type+"\"";
        return ret;

    def getRegexNamesAsParameters(self,startWithComma=False,withDefaultValues=False):
        ret = self._getParametersFromDict(self.regex, startWithComma, withDefaultValues);
        return ret
    
    

class XMLEventHandler(ContentHandler):  
    """Acts as a supply of information to help the builder in creating the product (a string representing a python module).
    The product can then be constructed by invoking :meth:`getpythonfile`.
    """  
    def __init__(self):
        self.commandBuilder = CommandBuilder();
    def startElement(self, tagname, attrs):
        if tagname == 'command': 
            self.commandBuilder.className = attrs.get('name', None)
            self.commandBuilder.superClass = attrs.get('is', None)
        if tagname == 'description': 
            self.commandBuilder.description = attrs.get('desc', None)
        if tagname == 'param': 
            name = attrs.get('name', None)
            defaultvalue = eval(attrs.get('default', None))
            self.commandBuilder.parameters[name] = defaultvalue
        if tagname == 'cmd': 
            self.commandBuilder.command = attrs.get('cmd', None)
        if tagname == 'regex': 
            name = attrs.get('name', None)
            regex = attrs.get('regex', None)
            matchnr = attrs.get('matchnr', 1)               
            type = attrs.get('type', 'int')               
            self.commandBuilder.regex[name] = RegExData(regex,matchnr,type)
        if tagname == 'message': 
            self.commandBuilder.message = attrs.get('text', None)
            
    def getpythonfile(self):
        # if None in self.options.keys() or None in self.options.values():
        #    print "Warning, unspecified attribute"
        return self.constructCachedCommand();
        

    def constructCachedCommand(self):    
        cache_duration = 60;
        if 'cache_duration' in self.commandBuilder.parameters:
            cache_duration = self.commandBuilder.parameters['cache_duration'];
            
        """initialize constructor event parameters"""
        description = self.commandBuilder.getDescription()
        constructorParametersC = self.commandBuilder.getConstructorParameters(startWithComma=True)
        instanceVariables = self.commandBuilder.getInstanceVariableAssignments()
        constructorParametersCV = self.commandBuilder.getConstructorParameters(startWithComma=True, withDefaultValues=True)
        parameters = self.commandBuilder.getConstructorParameterAssignments()
        searches = self.commandBuilder.getRegexSearches()
        regexVarListCV = self.commandBuilder.getRegexNamesAsParameters(startWithComma=True,withDefaultValues=True)
    
        #if len(self.commandBuilder.parameters) > 0:
        #    constructorParametersCV = ''.join([", %s='%s'" % (name,value) for (name,value) in self.commandBuilder.parameters.items() if type(value) is str]);
        #    constructorParametersCV += ''.join([", %s=%i" % (name,value) for (name,value) in self.commandBuilder.parameters.items() if not type(value) is str]);
    

        self.pythonfile = "\
from clusterbot.ssh import *\n\
from clusterbot.events.CachedEvent import CachedEvent\n\
from string import Template\n\
from clusterbot.util.timer import Timer\n\
\n\
class "+self.commandBuilder.className+"():\n\
    def __init__(self, name, tty"+constructorParametersC+", description='"+description+"' ):\n\
        self.description = description;\n\
        self.tty = tty;\n\
        self.name = name;\n\
        self.lastResult = None;\n\
        self.timer = Timer("+str(cache_duration)+");\n"\
+indentLines(instanceVariables,8)+"\
    def getDescription(self):\n\
        return self.description\n\
    def getName(self):\n\
        return self.name\n\
    def executeCommand(self, mess, args):\n\
        \"\"\" "+description+" \"\"\"\n\
        ret  = ''\n\
        if not self.lastResult == None and not self.timer.rings():\n\
            ret = self.lastResult;\n\
        else:\n\
            self.lastResult = None;\n\
            self.result = ranycmd(self.tty, '"+self.commandBuilder.command+"');\n\
            self.result = '\\n'.join(self.result)\n"\
+indentLines(searches,12)+"\
            self.result = Template('"+self.commandBuilder.message+"').safe_substitute(self.__dict__, result=self.result"+regexVarListCV+")\n\
            self.lastResult = self.result;\n\
            ret = self.result\n\
        return ret\n\
\n\
def returnInstance(tty, args):\n"\
+indentLines(parameters,4)+"\
    return "+self.commandBuilder.className+"('"+self.commandBuilder.className+"', tty"+constructorParametersCV+");";
        return self.pythonfile;

        
def parseCommand(xmlfile): 
    """Parse the file xmlfile and return a python module as a string"""
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

def createCommandFromFile(xmlfile): 
    """Parse the XML file and create a Python module with the name of the command"""
    parser = make_parser()
    xmleventhandler = XMLEventHandler()
    parser.setContentHandler(xmleventhandler)
    parser.parse(open(xmlfile))
    f = open('clusterbot/commandmodules/'+os.path.basename(xmleventhandler.commandBuilder.className)+".py", 'w');
    f.write(xmleventhandler.getpythonfile());
    return xmleventhandler.getpythonfile()

def createCommandFromString(xmlstring): 
    """Parse the string xmlstring and create a Python module with the name of the command"""
    parser = make_parser()
    xmleventhandler = XMLEventHandler()
    xml.sax.parseString(xmlstring,xmleventhandler)
    f = open('clusterbot/commandmodules/'+os.path.basename(xmleventhandler.commandBuilder.className)+".py", 'w');
    f.write(xmleventhandler.getpythonfile());
    return xmleventhandler.getpythonfile()
