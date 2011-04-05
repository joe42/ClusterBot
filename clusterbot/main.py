import getpass;
from clusterbot.util.MyXMLReader import MyXMLReader
from clusterbot.IdolJabberBot import IdolJabberBot
from clusterbot.features.IdolJabberBot_Broadcast import IdolJabberBot_Broadcast
from clusterbot.features.IdolJabberBot_DecoratorCommands import IdolJabberBot_DecoratorCommands
from clusterbot.features.IdolJabberBot_Shell import IdolJabberBot_Shell
from clusterbot.features.IdolJabberBot_SSHConnection import IdolJabberBot_SSHConnection
from clusterbot.features.IdolJabberBot_Whitelist import IdolJabberBot_Whitelist
from clusterbot.features.IdolJabberBot_XMLCommands import IdolJabberBot_XMLCommands
from clusterbot.features.IdolJabberBot_XMLEvents import IdolJabberBot_XMLEvents
from clusterbot.jabberbot import JabberBot

import sys 
import os


def getXMLConfigurationParameterWithDefault(config, tagname, attributeName):
    """:returns: The Value of the specified attribute if it exists and a default of "" otherwise."""
    try:
        return config.getAttribute(tagname, attributeName);
    except ValueError:
        return "";
    
def printUsageAndExit():
    print "Usage: python -m clusterbot.main [ xmlconfigfile ] [usepwd]";
    sys.exit(); 
    
def getConfigurationParameters():
    """:return: A tuple of configuration parameters"""         
    xmlFile =  os.path.dirname(__file__)+"/config.xml"
    headnodeIP = ""
    headnodeUser = ""
    headnodePW = "" #empty string is valid value for not using pwd
    jabberID = None
    jabberPW = None
    jabberWhitelist = None
    if len(sys.argv) == 2:
        if isXMLFile(sys.argv[1]):
            xmlFile = sys.argv[1];
        elif sys.argv[1] == "usepwd":
            print "Enter Password for the ssh account:"
            headnodePW = getpass.getpass();    
            print "Enter Password for the Jabber account:"
            jabberPW = getpass.getpass();    
    elif len(sys.argv) == 3:     
        if not isXMLFile(sys.argv[1]):
            printUsageAndExit();
        if not sys.argv[2] == "usepwd":
            printUsageAndExit();
        xmlFile = sys.argv[1];
        print "Enter Password for the ssh account:"
        headnodePW = getpass.getpass();    
        print "Enter Password for the Jabber account:"
        jabberPW = getpass.getpass();    
            
    config = MyXMLReader(xmlFile);
    #The defaults of "" allow for a connection via private key
    if headnodePW == None:
        heanodePW = getXMLConfigurationParameterWithDefault(config, "headnode", "password") 
    headnodeUser = getXMLConfigurationParameterWithDefault(config, "headnode","user")
    headnodeIP = config.getAttribute("headnode","ip");
    jabberID = config.getAttribute("jabber","jid");
    if jabberPW == None:
        jabberPW = config.getAttribute("jabber","password");
    jabberWhitelist = config.getAttribute("whitelist","jid");
            
    return (headnodeIP, headnodeUser, headnodePW, jabberID, jabberPW, jabberWhitelist)

def isXMLFile(file):
    return os.path.basename(sys.argv[1]).endswith(".xml");
    
if __name__ == "__main__":          
    headnodeIP, headnodeUser, headnodePW, jabberID, jabberPW, jabberWhitelist = getConfigurationParameters();
    bot = None
    print "ping frequency: "+str(JabberBot.PING_FREQUENCY)
    JabberBot.PING_FREQUENCY = 20
    print "ping frequency: "+str(JabberBot.PING_FREQUENCY)
    try:
        bot = IdolJabberBot(jabberID, jabberPW);
        whitelistFeature = IdolJabberBot_Whitelist(jabberWhitelist)
        broadcastFeature = IdolJabberBot_Broadcast()
        shellFeature = IdolJabberBot_Shell()
        sshConnectionFeature = IdolJabberBot_SSHConnection(headnodeIP, headnodeUser, headnodePW)
        decoratorCommandsFeature =  IdolJabberBot_DecoratorCommands()
        xmlCommandsFeature = IdolJabberBot_XMLCommands()
        xmlEventsFeature = IdolJabberBot_XMLEvents()
        bot.addFeature(whitelistFeature)
        bot.addFeature(broadcastFeature)
        bot.addFeature(sshConnectionFeature)
        bot.addFeature(decoratorCommandsFeature)
        bot.addFeature(shellFeature)
        bot.addFeature(xmlCommandsFeature)
        bot.addFeature(xmlEventsFeature)
        bot.initialize();
        bot.serve_forever(connect_callback = bot.connect_callback);
    finally:
        if bot:
            bot.quit()
