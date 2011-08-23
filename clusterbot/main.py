import getpass;
from clusterbot.util.MyXMLReader import MyXMLReader
from clusterbot.EventDrivenShellClusterBot import EventDrivenShellClusterBot
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
    if headnodePW == "":
        headnodePW = getXMLConfigurationParameterWithDefault(config, "headnode", "password") 
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
    #print "ping frequency: "+str(JabberBot.PING_FREQUENCY)
    JabberBot.PING_FREQUENCY = 20
    print "ping frequency: "+str(JabberBot.PING_FREQUENCY)
    try:
        bot = EventDrivenShellClusterBot(jabberID, jabberPW, headnodeIP, headnodeUser, headnodePW, debug=True) 
        bot.serve_forever(connect_callback = bot.connect_callback);
    finally:
        if bot:
            bot.quit()
