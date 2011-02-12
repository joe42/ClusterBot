from clusterbot.ClusterBot import ClusterBot
from clusterbot.shell.myconsole import MyConsole
from functools import partial
from jabberbot import botcmd
import xmpp
"""
Todo: manual import function X
import function for xml modules X
implement listevents X
implement anycommand in ssh X
load credentials and allowedJIDs from xml File X
"""

class ShellClusterBot(ClusterBot):
    """Allows for interactive shell-like sessions via xmpp.
    Take a look at :meth:`connect_callback` for an example on how to invoke ShellClusterBot. 
    """
    def __init__(self, jabberID, jabberPW, allowedJIDs, headnodeIP, headnodeUser, headnodePW, debug=False):
        super( ShellClusterBot, self ).__init__(jabberID, jabberPW, allowedJIDs, headnodeIP, headnodeUser, headnodePW, debug);
        self.shells = {}

    def connect_callback(self):
        """Register this callback to handle emulated shell commands.
        Must be called when connection to xmpp server is established and self.conn exists.
        Therefore it must be given as an argument to serve_forever after object creation like:
        .. highlight::
        bot = ShellClusterBot(jabberID, jabberPW, jabberWhitelist, headnodeIP, headnodeUser, headnodePW)
        bot.serve_forever(connect_callback = bot.connect_callback)
        bot.quit()
        """
        self.conn.RegisterHandler('message', self.callback_shell, makefirst=True)

    def quit(self):
        """Overwrites :meth:`clusterbot.ClusterBot.ClusterBot.quit`."""
        super( ShellClusterBot, self ).quit();
        for shell in self.shells.itervalues():
            if not shell.hasTerminated():
                shell.setTerminated()
            

    def callback_shell( self, conn, mess):
        """Handle shell connections."""
        # Prepare to handle either private chats or group chats
        type     = mess.getType()
        jid      = mess.getFrom()
        props    = mess.getProperties()
        text     = mess.getBody()
        username = self.get_sender_username(mess)
        
        
        
        #if no shell session is open for this jid let the other callbacks handle the request
        if not jid in self.shells:
            return
        
        self.debug("Shell command: %s" % text)
        if self.shells[jid].hasTerminated():
            self.shells.pop(jid)
            return
        
        if type not in ("groupchat", "chat"):
            self.debug("unhandled message type: %s" % type)
            return
        
        self.debug("*** props = %s" % props)
        self.debug("*** jid = %s" % jid)
        self.debug("*** username = %s" % username)
        self.debug("*** type = %s" % type)
        self.debug("*** text = %s" % text)
        
        # If a message format is not supported (eg. encrypted), txt will be None
        if not text: return
        
        # Remember the last-talked-in thread for replies
        self._JabberBot__threads[jid] = mess.getThread()
        
        self.shells[jid].sendcmd(text);
        raise xmpp.NodeProcessed

    @botcmd
    def opensession(self, mess, args): 
        """Execute any commands like in a shell. 
        Type end to end the session
        The syntax is: opensession [username] password
        """
        jid = mess.getFrom()
        if len(args.split(" ",1)) > 1:
            username, password = args.split(" ",1)
        elif len(args.split(" ",1)) == 1:
            username = self.headnodeUser
            password = args
        else:
            return "Login failed. Try help opensession for help."
        
        sendToSingleJID = partial(self.send, jid)
        self.shells[jid] = MyConsole(sendToSingleJID, self.headnodeIP, username, password)
        
        return "The session is established. Type end to stop the session.";

